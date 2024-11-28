#!/bin/bash


# A simple bash script to update the IP of a Cloudflare DNS A record. Acts as a DDNS


# Set to true if you want to export the whole response from Cloudflare DNS update
export_cloudflare_update_logs=false

# This is the Cloudflare zone (the name of the website on your Cloudflare)
zone=example.com

# This is the name of the A record that needs to be updated
dnsrecord=example.com

# ! Cloudflare authentication !
# ! Keep these private !
cloudflare_auth_email=email@gmail.com
cloudflare_auth_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


echo "################################################################"
echo  Datetime: $(date '+%d/%m/%Y %H:%M:%S')
echo "################################################################"


# Get the current public IP address
ip=$(dig +short myip.opendns.com @resolver1.opendns.com)

echo "Current Public IP Address: $ip"


# Get the zone id for the requested zone
zoneid=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$zone&status=active" \
  -H "X-Auth-Email: $cloudflare_auth_email" \
  -H "X-Auth-Key: $cloudflare_auth_key" \
  -H "Content-Type: application/json" | jq -r '{"result"}[] | .[0] | .id')

echo "Zone ID for $zone is $zoneid"


# Get the Cloudflare A record IP
cloudflare_ip=$(curl -s -X GET \
  --url https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records \
  --header "Content-Type: application/json" \
  --header "X-Auth-Email: $cloudflare_auth_email" \
  --header "X-Auth-Key: $cloudflare_auth_key" | jq -r '{"result"}[] | .[0] | .content')

echo "Current Cloudflare A record IP: $cloudflare_ip"


if [ $cloudflare_ip == $ip ]; then
  echo "Public IP and Cloudflare IP are the same, no changes needed"
  exit
fi


# Get the DNS record id
dnsrecordid=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records?type=A&name=$dnsrecord" \
  -H "X-Auth-Email: $cloudflare_auth_email" \
  -H "X-Auth-Key: $cloudflare_auth_key" \
  -H "Content-Type: application/json" | jq -r '{"result"}[] | .[0] | .id')

echo "DNS Record ID for $dnsrecord is $dnsrecordid"


# Update the IP of the A record
result=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zoneid/dns_records/$dnsrecordid" \
  -H "X-Auth-Email: $cloudflare_auth_email" \
  -H "X-Auth-Key: $cloudflare_auth_key" \
  -H "Content-Type: application/json" \
  --data "{\"type\":\"A\",\"name\":\"$dnsrecord\",\"content\":\"$ip\",\"proxied\":true}") 


if [ $(echo $result | jq -r '{"success"}[]') == "true" ]; then
  echo "Successfully updated the A record"
else
  echo "Failed to update the A record"
fi

if [ $export_cloudflare_update_logs == true ]; then
  echo $result | jq
fi

