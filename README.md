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
3.  **Run the script:**
    ```bash
    python fastlink/fastlink_checkin.py
    ```

#### Bash

1.  **Prerequisites:**
    - `curl`
    - `jq`
2.  **Configure credentials:**
    Open `fastlink/fastlink_checkin.sh` and fill in your `EMAIL` and `PASSWORD`.
3.  **Run the script:**
    ```bash
    bash fastlink/fastlink_checkin.sh
    ```