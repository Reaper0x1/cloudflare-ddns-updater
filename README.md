# Cloudflare DDNS Updater
Automatically update your Cloudflare A Record.
<p align="center">
  <img src="logo.png" alt=""/>
</p>

[![Docker Image - 1.0.0](https://img.shields.io/docker/v/reaper0x1/cloudflare-ddns-updater/latest?logo=docker&label=Docker%20Image)](https://hub.docker.com/r/reaper0x1/cloudflare-ddns-updater)
[![Github - Official](https://img.shields.io/badge/Github-Official-2dba4e?logo=github)](https://github.com/Reaper0x1/cloudflare-ddns-updater)
![Shell](https://img.shields.io/badge/Shell_Script-121011?style=flat&logo=gnu-bash&logoColor=white)

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Docker Environment Variables](#docker-environment-variables)
- [Getting Started](#getting-started-docker)  
    - [Prerequisities](#prerequisities)
    - [Docker Compose](#docker-compose)
    - [Docker Compose with .env file](#docker-compose-with-env-file)
    - [Build Locally](#build-locally)
- [Bash Script Usage](#bash-script-usage)  

## Description
This repository contains a Python script that dynamically updates a Cloudflare DNS "A" record with the machine's current public IP address. The script is intended to be run as a cron-like job, periodically checking the IP address and updating Cloudflare if a change is detected.

## Features
- Automatically fetches the public IP address of the local machine.
- Updates a specified Cloudflare DNS record if the public IP changes.
- Uses Cloudflare's API for secure DNS record management.
- Logs activity to both console and file.
- Configurable schedule using APScheduler with a cron-like syntax.
- Runs both locally with bash or in a container-friendly way.


## Docker Environment Variables

| **Variable**                | **Description**                                                | **Required** | **Default**       |
|-----------------------------|----------------------------------------------------------------|--------------|-------------------|
| `ZONE`                      | The Cloudflare zone (domain) to which the record belongs.                       | Yes          |                   |
| `DNS_RECORD`                | The A Record that needs to be updated.                         | Yes          |                   |
| `CLOUDFLARE_AUTH_EMAIL`     | Cloudflare account email for authentication.                  | Yes          |                   |
| `CLOUDFLARE_AUTH_KEY`       | Cloudflare API key for authentication.                        | Yes          |                   |
| `CRON_SCHEDULE`             | Cron schedule for updates (in cron format).                   | No           | `0 */6 * * *` (every 6 hours)     |
| `EXPORT_CF_UPDATE_ERROR_LOGS`| Log detailed Cloudflare API errors.                           | No           | `false`           |
| `EXECUTE_AT_START`          | Run the update when the script starts.                        | No           | `false`           |
| `TZ`                        | Timezone for logs.                                  | No           | `Europe/Berlin`   |
| `PUID`                      | User ID for file permissions (useful in containers).          | No           | `0` (root)            |
| `PGID`                      | Group ID for file permissions (useful in containers).         | No           | `0` (root)            |

## Getting Started (Docker)

### Prerequisities
1. 🐋 Docker must be installed and configured.
2. You need to set your Cloudflare environment variable:
    - `ZONE`: this is your domain, for example `mywebsite.com`
    - `DNS_RECORD`: you need to put the **Name** of your A Record, for example `mywebsite.com`.
    - `CLOUDFLARE_AUTH_KEY`: in the Cloudflare dashboard go to **Your Profile** > **API Token** > **Global API Key**

### Docker Compose
```yaml
services:
  cloudflare-ddns-updater:
    image: reaper0x1/cloudflare-ddns-updater:latest
    container_name: cloudflare-ddns-updater
    environment:
        # Put your cron schedule. 
        # You can generate one at https://crontab.guru/
        - CRON_SCHEDULE="0 */6 * * *"
        # Your timezone
        - TZ="Europe/Berlin"
        # Cloudflare
        - ZONE="site.com"
        - DNS_RECORD="site.com"
        - CLOUDFLARE_AUTH_EMAIL="mail@mail.com"
        - CLOUDFLARE_AUTH_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        # Set to true if you want to export the json response error during the update of A Record
        - EXPORT_CF_UPDATE_ERROR_LOGS="false"
        # Set to true if you want to start the script at the start of the container
        - EXECUTE_AT_START="false"
        # The users belongs to files.
        - PUID="1000"
        - PGID="1000"
    # Comment out the following two lines if logs are not needed
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Docker Compose with .env file
```yaml
services:
  cloudflare-ddns-updater:
    image: reaper0x1/cloudflare-ddns-updater:latest
    container_name: cloudflare-ddns-updater
    env_file: .env
    # Comment out the following two lines if logs are not needed
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

### Build Locally
```yaml
services:
  cloudflare-ddns-updater:
    build: .
    container_name: cloudflare-ddns-updater
    env_file: .env
    # Comment out the following two lines if logs are not needed
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## Bash Script Usage
This repository provides a bash script you can use if you don't want a Docker container.

1. Clone the repository:
    ```bash
    git clone https://github.com/Reaper0x1/cloudflare-ddns-updater && cd cloudflare-ddns-updater
    ```
2. You have to edit these variables inside the script:

    * **cloudflare_auth_email**: the email of your Cloudflare account
    * **cloudflare_auth_key**: you can get it by going into Your Profile > API Token > Global API Key
    * **zone**: your Cloudflare website
    * **dnsrecord**: the name of the A record
    * **(Optional)**: if you want to print out the whole Cloudflare response set **export_cloudflare_update_logs=true**
3. Run the script:
    ```bash
    ./ddns-updater.sh
    ```

    If you want to log everything simply redirect the output to a file:
    ```bash
    ./ddns-updater.sh > log.txt
    ```
4. (Optional) You can set up a cron job to run the script periodically.  
    1. Edit the crontable:
        ```bash
        crontab -e
        ```
    2. Add at the end of the file a line like the one below:
        ```
        0 */6 * * * /usr/bin/bash /path-to-script/ddns-updater.sh
    3. (Optional) Redirect output to a file:
        ```
        0 */6 * * * /usr/bin/bash /path-to-script/ddns-updater.sh >> /path-to-log/ddns-updater.log
        ```
    4. Save. You can check the cronjob with `crontab -l`
## License

[MIT](https://choosealicense.com/licenses/mit/)