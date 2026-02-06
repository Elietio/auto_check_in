import requests
import re
import json
import time
import random
import os
import sys
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file in the same directory as the script
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    print("Loading environment variables from .env file...")
    load_dotenv(dotenv_path=dotenv_path)

# Read credentials from environment variables
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

# Exit if credentials are not set
if not EMAIL or not PASSWORD:
    print("Error: EMAIL and PASSWORD environment variables must be set.", file=sys.stderr)
    print("Please create a .env file in the script's directory with your credentials.", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://cc01.fastlink.lat"

# 推送配置
# 推送方式: "serverchan" 或 "fcm"
PUSH_METHOD = "serverchan"

# ServerChan 配置 (从环境变量获取)
SERVERCHAN_UID = os.environ.get("SERVERCHAN_UID")
SERVERCHAN_SENDKEY = os.environ.get("SERVERCHAN_SENDKEY")

# FCM 配置 (从环境变量获取)
FCM_ENDPOINT = "https://us-central1-fir-cloudmessaging-4e2cd.cloudfunctions.net/send"
FCM_TOKEN = os.environ.get("FCM_TOKEN")
# -------------------

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': BASE_URL,
    'Referer': f'{BASE_URL}/auth/login',
    'X-Requested-With': 'XMLHttpRequest',
}

def send_notification_serverchan(title, desp, tags=None):
    """
    Sends a notification to ServerChan.
    """
    if not SERVERCHAN_SENDKEY:
        print("SERVERCHAN_SENDKEY environment variable not set, skipping notification.")
        return

    url = f"https://{SERVERCHAN_UID}.push.ft07.com/send/{SERVERCHAN_SENDKEY}.send"
    data = {
        'title': title,
        'desp': desp,
    }
    if tags:
        data['tags'] = tags
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()
        if result.get('code') == 0:
            print("ServerChan notification sent successfully.")
        else:
            print(f"Failed to send ServerChan notification: {result.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending notification: {e}")

def send_notification_fcm(title, message):
    """
    Sends a notification using Firebase Cloud Messaging.
    """
    if not FCM_TOKEN:
        print("FCM_TOKEN environment variable not set, skipping notification.")
        return
    
    url = FCM_ENDPOINT
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "data": {
            "to": FCM_TOKEN,
            "ttl": 60,
            "priority": "high",
            "data": {
                "text": {
                    "title": title,
                    "message": message,
                    "clipboard": False
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print("FCM notification sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending FCM notification: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

def send_notification(title, desp, tags=None):
    """
    Sends a notification using the configured method.
    """
    if PUSH_METHOD.lower() == "serverchan":
        send_notification_serverchan(title, desp, tags)
    elif PUSH_METHOD.lower() == "fcm":
        send_notification_fcm(title, desp)
    else:
        print(f"Unknown push method: {PUSH_METHOD}")

def random_delay(min_s=2, max_s=5):
    """Waits for a random duration between min_s and max_s seconds."""
    delay = random.uniform(min_s, max_s)
    print(f"Waiting for {delay:.2f} seconds to mimic human behavior...")
    time.sleep(delay)


def main():
    """
    Logs into Fastlink, performs check-in, and retrieves user info.
    """
    login_data = {
        'email': EMAIL,
        'passwd': PASSWORD,
        'code': ''
    }

    with requests.Session() as session:
        # 1. Login
        try:
            random_delay(60, 300)
            print("Attempting to log in...")
            login_response = session.post(
                f'{BASE_URL}/auth/login',
                headers=HEADERS,
                data=login_data
            )
            login_response.raise_for_status()

            # Handle verification if necessary
            if "访问验证" in login_response.text:
                print("Verification page detected. Submitting verification...")
                random_delay()
                verify_data = {'next': '/auth/login'}
                verify_response = session.post(
                    f'{BASE_URL}/verify',
                    headers=HEADERS,
                    data=verify_data
                )
                verify_response.raise_for_status()
                
                print("Verification submitted. Retrying login...")
                random_delay()
                # Retry login
                login_response = session.post(
                    f'{BASE_URL}/auth/login',
                    headers=HEADERS,
                    data=login_data
                )
                login_response.raise_for_status()

            login_json = login_response.json()
            print(f"Login successful: {login_json.get('msg', 'No message')}")
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"An error occurred during login: {e}")
            if 'login_response' in locals():
                print("Raw login response:")
                print(login_response.text)
            return

        # Update headers for subsequent requests
        session.headers.update({
            'Referer': f'{BASE_URL}/user',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        })

        # 2. Check-in
        checkin_message = ""
        try:
            random_delay()
            print("\nAttempting to check in...")
            checkin_response = session.post(f'{BASE_URL}/user/checkin', headers=session.headers)
            checkin_response.raise_for_status()
            checkin_json = checkin_response.json()
            checkin_message = checkin_json.get('msg', 'No message')
            print(f"Check-in successful: {checkin_message}")
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"An error occurred during check-in: {e}")

        # 3. Get user info
        try:
            random_delay()
            print("\nFetching user information...")
            user_response = session.get(f'{BASE_URL}/user', headers=session.headers)
            user_response.raise_for_status()
            user_response.encoding = 'utf-8' # Set encoding to UTF-8
            
            user_html = user_response.text
            
            # Use regex to find the required information
            traffic_pattern = r'"Unused_Traffic", "([^"]+)"'
            reset_date_pattern = r'"Traffic_RestDay", "([^"]+)"'
            today_usage_pattern = r'今日已用: (.*?)</'
            official_url_pattern = r'官网网址: <a href="([^"]+)"'
            backup_url_pattern = r'备用网址: <a href="([^"]+)"'
            domestic_url_pattern = r'国内加速: <a href="([^"]+)"'
            promo_code_pattern = r'优惠码: (\w+)'

            remaining_traffic = re.search(traffic_pattern, user_html)
            reset_date = re.search(reset_date_pattern, user_html)
            today_usage = re.search(today_usage_pattern, user_html)
            official_url = re.search(official_url_pattern, user_html)
            backup_url = re.search(backup_url_pattern, user_html)
            domestic_url = re.search(domestic_url_pattern, user_html)
            promo_code = re.search(promo_code_pattern, user_html)

            # Prepare notification content
            desp = f"- 签到信息: {checkin_message}\n"
            if remaining_traffic:
                desp += f"- 剩余流量: {remaining_traffic.group(1)}\n"
            if today_usage:
                desp += f"- 今日已用: {today_usage.group(1)}\n"
            if reset_date:
                desp += f"- 流量重置时间: {reset_date.group(1)}\n"
            if official_url:
                desp += f"- 官网网址: {official_url.group(1)}\n"
            if backup_url:
                desp += f"- 备用网址: {backup_url.group(1)}\n"
            if domestic_url:
                desp += f"- 国内加速: {domestic_url.group(1)}\n"
            if promo_code:
                desp += f"- 优惠码: {promo_code.group(1)}\n"

            print("\n--- Collected Information ---")
            print(desp)
            print("---------------------------")

            # Send notification
            send_notification("fastlink 签到", desp, tags="签到")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching user info: {e}")
            if 'user_response' in locals():
                print("Raw user info response:")
                print(user_response.text)

if __name__ == "__main__":
    main()
