#!/bin/bash

# --- Configuration ---
EMAIL="YOUR_EMAIL_HERE"
PASSWORD="YOUR_PASSWORD_HERE"
BASE_URL="https://cc01.fastlink.lat"
SERVERCHAN_UID="YOUR_SERVERCHAN_UID_HERE"
SERVERCHAN_SENDKEY="YOUR_SERVERCHAN_SENDKEY_HERE"
# -------------------

# URL encode the credentials
URL_ENCODED_EMAIL=$(printf %s "$EMAIL" | jq -s -R -r @uri)
URL_ENCODED_PASSWORD=$(printf %s "$PASSWORD" | jq -s -R -r @uri)

COOKIE_JAR=$(mktemp) # Create a temporary file for cookies

# Headers
LOGIN_HEADERS=(
  -H 'accept: application/json, text/javascript, */*; q=0.01'
  -H 'accept-language: en-US,en;q=0.9'
  -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8'
  -H "origin: ${BASE_URL}"
  -H "referer: ${BASE_URL}/auth/login"
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
  -H 'x-requested-with: XMLHttpRequest'
)

CHECKIN_HEADERS=(
  -H 'accept: application/json, text/javascript, */*; q=0.01'
  -H 'accept-language: en-US,en;q=0.9'
  -H "origin: ${BASE_URL}"
  -H "referer: ${BASE_URL}/user"
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
  -H 'x-requested-with: XMLHttpRequest'
)

USER_INFO_HEADERS=(
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
  -H 'accept-language: en-US,en;q=0.9'
  -H "origin: ${BASE_URL}"
  -H "referer: ${BASE_URL}/user"
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
)

# Function to URL encode strings for ServerChan
urlencode() {
  local string="$1"
  echo -n "$string" | jq -s -R -r @uri
}

# Function to send notification to ServerChan
send_notification() {
  local title="$1"
  local desp="$2"
  local tags="$3"
  
  if [ -z "$SERVERCHAN_SENDKEY" ]; then
    echo "ServerChan SendKey not configured, skipping notification."
    return
  fi
  
  # ServerChan 使用 Markdown 格式，我们需要确保换行正确
  # 不需要转换换行符，直接使用原始格式
  
  # URL encode parameters
  local encoded_title=$(urlencode "$title")
  local encoded_desp=$(urlencode "$desp")
  local encoded_tags=$(urlencode "$tags")
  
  echo "Sending notification to ServerChan..."
  local response=$(curl -s -X POST \
    "https://${SERVERCHAN_UID}.push.ft07.com/send/${SERVERCHAN_SENDKEY}.send" \
    -d "title=${encoded_title}&desp=${encoded_desp}&tags=${encoded_tags}")
  
  # Check if notification was sent successfully
  if [[ "$response" == *'"code":0'* ]]; then
    echo "ServerChan notification sent successfully."
  else
    echo "Failed to send ServerChan notification: $response"
  fi
}

# 1. Login
echo "$(date '+%Y-%m-%d %H:%M:%S') Attempting to log in..."
LOGIN_RESPONSE=$(curl -s -c "$COOKIE_JAR" "${LOGIN_HEADERS[@]}" --data-raw "email=${URL_ENCODED_EMAIL}&passwd=${URL_ENCODED_PASSWORD}&code=" "${BASE_URL}/auth/login")

# Check for login success
if [[ "$LOGIN_RESPONSE" == *'"ret":1'* ]]; then
  LOGIN_MSG=$(echo "$LOGIN_RESPONSE" | jq -r .msg)
  echo "Login successful: $LOGIN_MSG"

  # 2. Check-in
  echo -e "\nAttempting to check in..."
  CHECKIN_RESPONSE=$(curl -s -X POST -b "$COOKIE_JAR" "${CHECKIN_HEADERS[@]}" "${BASE_URL}/user/checkin")
  CHECKIN_MSG=$(echo "$CHECKIN_RESPONSE" | jq -r .msg)
  echo "Check-in response: $CHECKIN_MSG"
  
  # 3. Get user info
  echo -e "\nFetching user information..."
  USER_RESPONSE=$(curl -s -b "$COOKIE_JAR" "${USER_INFO_HEADERS[@]}" "${BASE_URL}/user")
  
  # Extract information using grep and sed
  REMAINING_TRAFFIC=$(echo "$USER_RESPONSE" | grep -o '"Unused_Traffic", "[^"]*"' | sed 's/"Unused_Traffic", "\(.*\)"/\1/')
  RESET_DATE=$(echo "$USER_RESPONSE" | grep -o '"Traffic_RestDay", "[^"]*"' | sed 's/"Traffic_RestDay", "\(.*\)"/\1/')
  TODAY_USAGE=$(echo "$USER_RESPONSE" | grep -o '今日已用: .*</' | sed 's/今日已用: \(.*\)<\//\1/')
  OFFICIAL_URL=$(echo "$USER_RESPONSE" | grep -o '官网网址: <a href="[^"]*"' | sed 's/官网网址: <a href="\(.*\)"/\1/')
  BACKUP_URL=$(echo "$USER_RESPONSE" | grep -o '备用网址: <a href="[^"]*"' | sed 's/备用网址: <a href="\(.*\)"/\1/')
  DOMESTIC_URL=$(echo "$USER_RESPONSE" | grep -o '国内加速: <a href="[^"]*"' | sed 's/国内加速: <a href="\(.*\)"/\1/')
  PROMO_CODE=$(echo "$USER_RESPONSE" | grep -o '优惠码: \w\+' | sed 's/优惠码: \(.*\)/\1/')
  
  # Prepare notification content - 使用 Markdown 格式
  NOTIFICATION_CONTENT="- 签到信息: $CHECKIN_MSG
"
  if [ ! -z "$REMAINING_TRAFFIC" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 剩余流量: $REMAINING_TRAFFIC
"
  fi
  if [ ! -z "$TODAY_USAGE" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 今日已用: $TODAY_USAGE
"
  fi
  if [ ! -z "$RESET_DATE" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 流量重置时间: $RESET_DATE
"
  fi
  if [ ! -z "$OFFICIAL_URL" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 官网网址: $OFFICIAL_URL
"
  fi
  if [ ! -z "$BACKUP_URL" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 备用网址: $BACKUP_URL
"
  fi
  if [ ! -z "$DOMESTIC_URL" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 国内加速: $DOMESTIC_URL
"
  fi
  if [ ! -z "$PROMO_CODE" ]; then
    NOTIFICATION_CONTENT="${NOTIFICATION_CONTENT}- 优惠码: $PROMO_CODE"
  fi
  echo -e "\n--- Collected Information ---"
  echo -e "$NOTIFICATION_CONTENT"
  echo "----------------------------"
  
  # Send notification
  send_notification "fastlink 签到" "$NOTIFICATION_CONTENT" "签到"
  
else
  echo "Login failed. Response:"
  echo "$LOGIN_RESPONSE"
fi

# Clean up the cookie jar
rm "$COOKIE_JAR"