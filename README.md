# Auto Check-in Scripts

A collection of personal automation scripts for daily check-ins and other tasks.

## Fastlink Daily Check-in

This script automates the daily check-in process for Fastlink to claim daily rewards. It supports both Python and Bash execution environments.

### 1. Initial Setup

Before running the script for the first time, you need to configure your credentials.

1.  **Find the template file:** Navigate to the `fastlink` directory. You will find a file named `.env.example`.

2.  **Create your configuration file:** Create a copy of this file and name it `.env`.
    ```bash
    cp fastlink/.env.example fastlink/.env
    ```

3.  **Edit the `.env` file:** Open `fastlink/.env` with a text editor and fill in your Fastlink `EMAIL` and `PASSWORD`.

    ```dotenv
    # fastlink/.env

    # Your FastLink email
    EMAIL="YOUR_EMAIL_HERE"

    # Your FastLink password
    PASSWORD="YOUR_PASSWORD_HERE"
    ```
    This file is ignored by Git, so your credentials will not be committed.

### 2. Running the Script

You can choose to run either the Python or the Bash version of the script.

---

#### **Option A: Using Python**

This is the recommended method as it provides more detailed feedback and error handling.

1.  **Install Dependencies:**
    Make sure you have Python 3 installed. Then, install the required packages using `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Script:**
    Execute the Python script from the project's root directory.
    ```bash
    python fastlink/fastlink_checkin.py
    ```

---

#### **Option B: Using Bash**

A lightweight option if you prefer not to use Python.

1.  **Prerequisites:**
    Ensure you have `curl` and `jq` installed on your system. You can usually install them with your system's package manager (e.g., `apt-get install curl jq` or `brew install curl jq`).

2.  **Run the Script:**
    Execute the Bash script from the project's root directory.
    ```bash
    bash fastlink/fastlink_checkin.sh
    ```

### 3. (Optional) Push Notifications

You can receive a notification every time the script runs.

1.  **Configuration:**
    Uncomment and fill in the notification service details in your `fastlink/.env` file.

    - **For [ServerChan](https://sc3.ft07.com/):**
        ```dotenv
        SERVERCHAN_UID="Your_UID"
        SERVERCHAN_SENDKEY="Your_SendKey"
        ```
    - **For [FCM Toolbox](https://fcm-toolbox-public.web.app/):**
        ```dotenv
        FCM_TOKEN="Your_FCM_Token"
        ```
2.  **Enable in Script:**
    In either `fastlink_checkin.py` or `fastlink_checkin.sh`, set the `PUSH_METHOD` variable to `"serverchan"` or `"fcm"` to enable your chosen service.

---
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