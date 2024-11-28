import os
import pwd
import grp
import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import logging


# Env variables
ZONE = os.getenv("ZONE")
DNS_RECORD = os.getenv("DNS_RECORD")
CLOUDFLARE_AUTH_EMAIL = os.getenv("CLOUDFLARE_AUTH_EMAIL")
CLOUDFLARE_AUTH_KEY = os.getenv("CLOUDFLARE_AUTH_KEY")
EXPORT_CF_UPDATE_ERROR_LOGS = (
    os.getenv("EXPORT_CF_UPDATE_ERROR_LOGS", "false").lower() == "true"
)
EXECUTE_AT_START = os.getenv("EXECUTE_AT_START", "false").lower() == "true"
TZ = os.getenv("TZ", "Europe/Berlin")
PUID = os.getenv("PUID", "0")
PGID = os.getenv("PGID", "0")


# Configuration
LOG_FOLDER = "/app/logs"
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
LOG_FILE_NAME = f"{CURRENT_DATE}.log"
LOG_FULL_PATH = os.path.join(LOG_FOLDER, LOG_FILE_NAME)
SCHEDULER_ERROR_LOG_PATH = os.path.join(LOG_FOLDER, "scheduler.log")


# Create logs folder if not exists
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)


class CustomFileHandler(logging.FileHandler):
    def __init__(
        self, filename, mode="a", encoding=None, delay=False, user=None, group=None
    ):
        super().__init__(filename, mode, encoding, delay)
        if user and group:
            self.set_owner_group(filename, user, group)

    def set_owner_group(self, filename, user, group):
        try:
            uid = pwd.getpwnam(user).pw_uid
            gid = grp.getgrnam(group).gr_gid
            os.chown(filename, uid, gid)
        except KeyError as e:
            print(f"User not found: {e}")
        except PermissionError as e:
            print(
                f"Insufficient permissions to change the owner/group of the file: {e}"
            )


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        CustomFileHandler(LOG_FULL_PATH, user=PUID, group=PGID),
        logging.StreamHandler(),  # Console log
    ],
)


# Function to change permission recursively
def chown_recursive(path, uid, gid):
    if isinstance(uid, str):
        uid = int(uid)

    if isinstance(gid, str):
        gid = int(gid)

    for root, dirs, files in os.walk(path):
        os.chown(root, uid, gid)
        for file in files:
            os.chown(os.path.join(root, file), uid, gid)


# Function to fetch the current public IP address
def fetch_public_ip():
    logging.info("Fetching current public IP address...")
    response = requests.get("https://api64.ipify.org")
    response.raise_for_status()
    ip = response.text.strip()
    logging.info(f"Current public IP address: {ip}")
    return ip


# Function to fetch the Zone ID from Cloudflare
def fetch_zone_id(zone):
    logging.info(f"Fetching Zone ID for {zone}...")
    response = requests.get(
        "https://api.cloudflare.com/client/v4/zones",
        headers={
            "X-Auth-Email": CLOUDFLARE_AUTH_EMAIL,
            "X-Auth-Key": CLOUDFLARE_AUTH_KEY,
            "Content-Type": "application/json",
        },
        params={"name": zone, "status": "active"},
    )
    response.raise_for_status()
    data = response.json()
    zone_id = data["result"][0]["id"]
    logging.info(f"Zone ID for {zone}: {zone_id}")
    return zone_id


# Function to fetch the current A record's IP and ID
def fetch_a_record(zone_id, dns_record):
    logging.info("Fetching current A record IP from Cloudflare...")
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
        headers={
            "X-Auth-Email": CLOUDFLARE_AUTH_EMAIL,
            "X-Auth-Key": CLOUDFLARE_AUTH_KEY,
            "Content-Type": "application/json",
        },
        params={"type": "A", "name": dns_record},
    )
    response.raise_for_status()
    data = response.json()

    if len(data["result"]) == 0:
        logging.error(
            "There was an error fetching the current A record IP address, check your DNS_RECORD."
        )
        exit(-1)

    dns_record_id = data["result"][0]["id"]
    cloudflare_ip = data["result"][0]["content"]
    logging.info(f"Current Cloudflare A record IP: {cloudflare_ip}")
    return dns_record_id, cloudflare_ip


# Function to update the A record on Cloudflare
def update_a_record(zone_id, dns_record_id, ip, dns_record):
    logging.info("Updating Cloudflare A record...")
    response = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{dns_record_id}",
        headers={
            "X-Auth-Email": CLOUDFLARE_AUTH_EMAIL,
            "X-Auth-Key": CLOUDFLARE_AUTH_KEY,
            "Content-Type": "application/json",
        },
        json={"type": "A", "name": dns_record, "content": ip, "proxied": True},
    )
    response.raise_for_status()
    data = response.json()
    if data["success"]:
        logging.info("[✓] Successfully updated the A record!")
    else:
        logging.error("[✕] Failed to update the A record!")
        if EXPORT_CF_UPDATE_ERROR_LOGS:
            logging.info(data)

    return data["success"]


# Main function
def update_dns():

    # Update permissions

    logging.info("###############################################################")
    logging.info("########### Updating Cloudflare DNS A Record (DDNS) ###########")
    logging.info("###############################################################")

    # Fetch the public IP
    public_ip = fetch_public_ip()

    # Retrieve the Zone ID
    zone_id = fetch_zone_id(ZONE)

    # Fetch the current A record's IP and ID
    dns_record_id, cloudflare_ip = fetch_a_record(zone_id, DNS_RECORD)

    # Compare the public IP with the Cloudflare IP
    if cloudflare_ip == public_ip:
        logging.info("[=] Public IP and Cloudflare IP are the same, no update needed.")
        return

    # Update the A record if the IPs differ
    update_a_record(zone_id, dns_record_id, public_ip, DNS_RECORD)


def start_update():
    update_dns()
    next_run = scheduler.get_job("update_ddns_job").next_run_time
    logging.info(f"Next execution: {next_run}")


if __name__ == "__main__":

    # Update folder permission
    chown_recursive(LOG_FOLDER, PUID, PGID)

    # Execute an update at the script start
    if EXECUTE_AT_START:
        logging.info(f"Starting the script before scheduler...")
        update_dns()

    # Scheduler configuration
    scheduler = BlockingScheduler()

    cron_schedule = os.getenv("CRON_SCHEDULE", "0 */6 * * *")
    logging.info(f'Starting script with schedule: "{cron_schedule}"')

    # APScheduler notaion converter
    minute, hour, day, month, day_of_week = cron_schedule.split()
    scheduler.add_job(
        start_update,  # Wrapper
        "cron",
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        id="update_ddns_job",
    )

    # Specific logger for APScheduler
    scheduler_logger = logging.getLogger("apscheduler")
    scheduler_logger.setLevel(logging.ERROR)
    scheduler_logger.addHandler(
        CustomFileHandler(SCHEDULER_ERROR_LOG_PATH, user=PUID, group=PGID)
    )

    # Start the scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler exited.")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
