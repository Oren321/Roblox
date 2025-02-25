import requests
import time
import argparse
from colorama import Fore, Style

# Constants for readability
VALID, TAKEN, CENSORED = 0, 1, 2

# Use a persistent session for better performance
session = requests.Session()

# Load webhook URL from a file (safer than hardcoding)
try:
    with open("webhook_url.txt", "r") as file:
        WEBHOOK_URL = file.read().strip()
except FileNotFoundError:
    WEBHOOK_URL = None
    print(Fore.RED + "ERROR: webhook_url.txt not found. Valid usernames won't be sent to Discord." + Style.RESET_ALL)

def send_to_discord(username):
    """Sends a valid username to the Discord webhook."""
    if not WEBHOOK_URL:
        return

    payload = {
        "content": f"🎉 **VALID USERNAME FOUND!** `{username}` is available!"
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        print(Fore.CYAN + f"✅ Sent to Discord: {username}" + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Failed to send to Discord: {e}" + Style.RESET_ALL)

def check_username(username):
    """Checks if a given Roblox username is available, taken, or censored."""
    url = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
    
    try:
        response = session.get(url, timeout=5)  # Added timeout for reliability
        response.raise_for_status()  # Raise exception for HTTP errors (4xx, 5xx)
        response_data = response.json()

        code = response_data.get("code", -1)  # Default to -1 if code is missing
        status_messages = {
            VALID: Fore.GREEN + "VALID",
            TAKEN: Fore.LIGHTBLACK_EX + "TAKEN",
            CENSORED: Fore.RED + "CENSORED",
        }
        
        status = status_messages.get(code, Fore.YELLOW + f"UNKNOWN ({code})")
        print(f"{status}: {username}" + Style.RESET_ALL)

        if code == VALID:
            send_to_discord(username)  # Send valid username to Discord

    except requests.exceptions.Timeout:
        print(Fore.YELLOW + f"TIMEOUT: {username}" + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        print(Fore.YELLOW + f"ERROR: {username} - {e}" + Style.RESET_ALL)

def main():
    """Reads a list of usernames from a file and checks each one."""
    parser = argparse.ArgumentParser(description="Check Roblox usernames.")
    parser.add_argument("-f", "--file", default="usernames.txt", help="File containing usernames")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as file:
            usernames = file.read().splitlines()

        for username in usernames:
            if username.strip():  # Skip empty lines
                check_username(username)
                time.sleep(0.05)

    except FileNotFoundError:
        print(Fore.RED + f"ERROR: File '{args.file}' not found!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
