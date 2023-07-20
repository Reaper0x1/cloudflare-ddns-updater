# Cloudflare DDNS Updater

A simple script to update the IP address of a Cloudflare A record.

## Installation

Clone the repository:

```bash
git clone https://github.com/Reaper0x1/cloudflare_ddns_updater.git
```

## Configuration

You have to edit these variables:

* **cloudflare_auth_email**: the email of your Cloudflare account
* **cloudflare_auth_key**: you can get it by going into Your Profile > API Token > Global API Key
* **zone**: your Cloudflare website
* **dnsrecord**: the name of the A record

**Optional**: if you want to print out the whole Cloudflare response set **export_cloudflare_update_logs=true**

## Usage

Run the script
```bash
./cloudflare-ddns-updater.sh
```

If you want to log everything simply redirect the output to a file:
```bash
./cloudflare-ddns-updater.sh > log.txt
```

## License

[MIT](https://choosealicense.com/licenses/mit/)