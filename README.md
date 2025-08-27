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
    - Set `PUSH_METHOD` to either "serverchan" or "fcm"
    - For ServerChan: Fill in your `SERVERCHAN_UID` and `SERVERCHAN_SENDKEY`
    - For FCM: Fill in your `FCM_TOKEN`
4.  **Run the script:**
    ```bash
    python fastlink/fastlink_checkin.py
    ```

#### Bash

1.  **Prerequisites:**
    - `curl`
    - `jq`
2.  **Configure credentials:**
    Open `fastlink/fastlink_checkin.sh` and fill in your `EMAIL` and `PASSWORD`.
3.  **Configure push notifications (optional):**
    - Set `PUSH_METHOD` to either "serverchan" or "fcm"
    - For ServerChan: Fill in your `SERVERCHAN_UID` and `SERVERCHAN_SENDKEY`
    - For FCM: Fill in your `FCM_TOKEN`
4.  **Run the script:**
    ```bash
    bash fastlink/fastlink_checkin.sh
    ```

### Push Notifications

The script supports two methods for push notifications:

1. **ServerChan**
   - A free push service that sends notifications to WeChat
   - Requires a UID and SendKey from [ServerChan](https://sc3.ft07.com/)

2. **Firebase Cloud Messaging (FCM)**
   - Google's cross-platform messaging solution
   - Requires an FCM token for your device
   - You can get your FCM token and test push notifications using [FCM Toolbox](https://fcm-toolbox-public.web.app/)

You can choose which method to use by setting the `PUSH_METHOD` variable in the configuration section.

## Let's Encrypt

This script automates the renewal of Let's Encrypt certificates.

### Usage

1.  **Configure the script:**
    Open `letsencrypt/renew.sh` and configure the following variables:
    - `DOMAINS_TO_CHECK`: A comma-separated list of domains to check (e.g., "example.com,www.example.com").
    - `FCM_TOKEN`: Your FCM token for push notifications.

2.  **Run the script manually:**
    ```bash
    bash letsencrypt/renew.sh
    ```

3.  **Set up Cronjob for automatic renewal:**
    To run the script automatically every Saturday at 9:00 AM, add the following line to your crontab:
    ```
    0 9 * * 6 /bin/bash /path/to/your/project/auto_check_in/letsencrypt/renew.sh
    ```
    **Note:** Make sure to replace `/path/to/your/project/` with the actual absolute path to the project directory.
