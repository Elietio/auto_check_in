# auto_check_in
Self-used check-in script

## Fastlink

This script automates the daily check-in process for Fastlink.

### Usage

#### Python

1.  **Install dependencies:**
    ```bash
    pip install requests
    ```
2.  **Configure credentials:**
    Open `fastlink/fastlink_checkin.py` and fill in your `EMAIL` and `PASSWORD`.
3.  **Configure push notifications (optional):**
    - Set `PUSH_METHOD` in the script to either "serverchan" or "fcm".
    - Set the required environment variables:
      - `SERVERCHAN_UID` and `SERVERCHAN_SENDKEY` (for ServerChan)
      - `FCM_TOKEN` (for FCM)
4.  **Run the script:**
    ```bash
    export SERVERCHAN_SENDKEY="your_key"
    python fastlink/fastlink_checkin.py
    ```

#### Bash

1.  **Prerequisites:**
    - `curl`
    - `jq`
2.  **Configure credentials:**
    Open `fastlink/fastlink_checkin.sh` and fill in your `EMAIL` and `PASSWORD`.
3.  **Configure push notifications (optional):**
    - Set `PUSH_METHOD` in the script to either "serverchan" or "fcm".
    - Set the required environment variables:
      - `SERVERCHAN_UID` and `SERVERCHAN_SENDKEY` (for ServerChan)
      - `FCM_TOKEN` (for FCM)
4.  **Run the script:**
    ```bash
    export FCM_TOKEN="your_token"
    bash fastlink/fastlink_checkin.sh
    ```

### Push Notifications

The script supports two methods for push notifications:

1. **ServerChan**
   - A free push service that sends notifications to WeChat.
   - Requires `SERVERCHAN_UID` and `SERVERCHAN_SENDKEY` environment variables. Get them from [ServerChan](https://sc3.ft07.com/).

2. **Firebase Cloud Messaging (FCM)**
   - Google's cross-platform messaging solution.
   - Requires `FCM_TOKEN` environment variable.
   - You can get your FCM token and test push notifications using [FCM Toolbox](https://fcm-toolbox-public.web.app/).

## Let's Encrypt

This script automates the renewal of Let's Encrypt certificates.

### Usage

1.  **Configure the script:**
    - Open `letsencrypt/renew.sh` and configure `DOMAINS_TO_CHECK` (e.g., "example.com,www.example.com").
    - Set the `FCM_TOKEN` environment variable for push notifications.

2.  **Run the script manually:**
    ```bash
    export FCM_TOKEN="your_token"
    bash letsencrypt/renew.sh
    ```

3.  **Set up Cronjob for automatic renewal:**
    To run the script automatically every Saturday at 9:00 AM, add the following line to your crontab (make sure to include environment variables if they are not set globally):
    ```
    0 9 * * 6 FCM_TOKEN="your_token" /bin/bash /path/to/your/project/auto_check_in/letsencrypt/renew.sh
    ```
    **Note:** Make sure to replace `/path/to/your/project/` with the actual absolute path to the project directory.
