#!/bin/bash

# --- Configuration ---
# Comma-separated list of domains to check
DOMAINS_TO_CHECK="www.elietio.xyz,shiki.elietio.tk"
# Expiry threshold in days
EXPIRY_THRESHOLD=10

# FCM Configuration
FCM_ENDPOINT="https://us-central1-fir-cloudmessaging-4e2cd.cloudfunctions.net/send"
# Replace with your FCM token
FCM_TOKEN="YOUR_FCM_TOKEN"
# --- End of Configuration ---

# Function to send notification using FCM
send_notification_fcm() {
  local title="$1"
  local message="$2"

  if [ -z "$FCM_TOKEN" ] || [ "$FCM_TOKEN" == "YOUR_FCM_TOKEN" ]; then
    echo "FCM Token not configured, skipping notification."
    return
  fi

  echo "Sending notification via FCM..."

  # Escape the message content to avoid JSON format errors
  local escaped_title=$(echo "$title" | sed 's/"/\"/g')
  local escaped_message=$(echo "$message" | sed 's/"/\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')

  # Use the same JSON structure as in fcm-push.md
  local payload='''{
    "data": {
      "to": "'''$FCM_TOKEN'''",
      "ttl": 60,
      "priority": "high",
      "data": {
        "text": {
          "title": "'''$escaped_title'''",
          "message": "'''$escaped_message'''",
          "clipboard": false
        }
      }
    }
  }'''

  local response=$(curl -s -X POST "${FCM_ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d "$payload")

  echo "FCM response: $response"

  # Check if the response was successful
  if [[ "$response" != *"error"* ]]; then
    echo "FCM notification sent successfully."
  else
    echo "Failed to send FCM notification. Response: $response"
  fi
}

# --- Main Script ---
NEEDS_RENEWAL=false

# Check certificate expiry for each domain
IFS=',' read -ra DOMAIN_ARRAY <<< "$DOMAINS_TO_CHECK"
for cert_name in "${DOMAIN_ARRAY[@]}"; do
  echo "Checking certificate for: $cert_name"
  
  # Get certificate info
  cert_info=$(certbot certificates -d "$cert_name" 2>/dev/null)
  
  if [ -z "$cert_info" ]; then
    echo "Could not find certificate for $cert_name"
    continue
  fi

  # Extract expiry date
  expiry_date_str=$(echo "$cert_info" | grep "Expiry Date" | sed -E 's/.*Expiry Date: ([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/')
  
  if [ -z "$expiry_date_str" ]; then
      echo "Could not extract expiry date for $cert_name"
      continue
  fi

  # Convert expiry date to seconds since epoch
  expiry_date_seconds=$(date -d "$expiry_date_str" +%s)
  current_date_seconds=$(date +%s)
  
  # Calculate days until expiry
  days_until_expiry=$(( (expiry_date_seconds - current_date_seconds) / 86400 ))
  
  echo "Certificate for $cert_name expires in $days_until_expiry days."

  if [ "$days_until_expiry" -lt "$EXPIRY_THRESHOLD" ]; then
    NEEDS_RENEWAL=true
    echo "Certificate for $cert_name needs renewal."
  fi
done

# If any certificate needs renewal, run the renewal process
if [ "$NEEDS_RENEWAL" = true ]; then
  echo "One or more certificates need renewal. Starting renewal process..."
  
  # 1. Stop Nginx
  echo "Stopping Nginx..."
  service nginx stop
  
  # 2. Renew certificates
  echo "Renewing certificates..."
  renew_output=$(certbot renew 2>&1)
  echo "$renew_output"
  
  # 3. Start Nginx
  echo "Starting Nginx..."
  service nginx start
  
  # 4. Check Nginx status
  nginx_status=$(service nginx status)
  
  # 5. Send notification
  notification_title="Let's Encrypt Certificate Renewal"
  notification_message="Certificate renewal process finished.\n\nRenewal Output:\n$renew_output\n\nNginx Status:\n$nginx_status"
  send_notification_fcm "$notification_title" "$notification_message"
  
else
  echo "All certificates are up to date. No renewal needed."
fi

echo "Script finished."
