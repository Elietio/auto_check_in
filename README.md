# auto_check
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
   - You can get your FCM token using [FCM Toolbox](https://fcm-toolbox-public.web.app/)

You can choose which method to use by setting the `PUSH_METHOD` variable in the configuration section.