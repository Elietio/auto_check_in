#!/bin/bash

# --- Configuration ---
EMAIL="YOUR_EMAIL_HERE"
PASSWORD="YOUR_PASSWORD_HERE"
# -------------------

# URL encode the credentials
URL_ENCODED_EMAIL=$(printf %s "$EMAIL" | jq -s -R -r @uri)
URL_ENCODED_PASSWORD=$(printf %s "$PASSWORD" | jq -s -R -r @uri)

BASE_URL="https://cc01.fastlink.lat"
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

# 1. Login
echo "$(date '+%Y-%m-%d %H:%M:%S') Attempting to log in..."
LOGIN_RESPONSE=$(curl -s -c "$COOKIE_JAR" "${LOGIN_HEADERS[@]}" --data-raw "email=${URL_ENCODED_EMAIL}&passwd=${URL_ENCODED_PASSWORD}&code=" "${BASE_URL}/auth/login")

# Check for login success (basic check, can be improved)
if [[ "$LOGIN_RESPONSE" == *'"ret":1'* ]]; then
  echo "Login successful: $(echo "$LOGIN_RESPONSE" | jq -r .msg)"

  # 2. Check-in
  echo -e "\nAttempting to check in..."
  CHECKIN_RESPONSE=$(curl -s -X POST -b "$COOKIE_JAR" "${CHECKIN_HEADERS[@]}" "${BASE_URL}/user/checkin")
  echo "Check-in response: $(echo "$CHECKIN_RESPONSE" | jq -r .msg)"
else
  echo "Login failed. Response:"
  echo "$LOGIN_RESPONSE"
fi

# Clean up the cookie jar
rm "$COOKIE_JAR"