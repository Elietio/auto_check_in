import requests

# --- Configuration ---
EMAIL = "YOUR_EMAIL_HERE"
PASSWORD = "YOUR_PASSWORD_HERE"
BASE_URL = "https://cc01.fastlink.lat"
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

def main():
    """
    Logs into Fastlink and performs the daily check-in.
    """
    

    login_data = {
        'email': EMAIL,
        'passwd': PASSWORD,
        'code': ''
    }

    # Use a session object to persist cookies
    with requests.Session() as session:
        # 1. Login
        print("Attempting to log in...")
        try:
            login_response = session.post(
                f'{BASE_URL}/auth/login',
                headers=HEADERS,
                data=login_data
            )
            login_response.raise_for_status()  # Raise an exception for bad status codes
            login_json = login_response.json()
            print(f"Login successful: {login_json.get('msg', 'No message')}")

            # Update referer for the next request
            session.headers.update({'Referer': f'{BASE_URL}/user'})

            # 2. Check-in
            print("\nAttempting to check in...")
            checkin_response = session.post(f'{BASE_URL}/user/checkin', headers=session.headers)
            checkin_response.raise_for_status()
            checkin_json = checkin_response.json()
            print(f"Check-in successful: {checkin_json.get('msg', 'No message')}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        except ValueError: # Catches JSON decoding errors
            print("Failed to decode JSON response. Raw response:")
            print(login_response.text if 'login_response' in locals() else checkin_response.text)


if __name__ == "__main__":
    main()