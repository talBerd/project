import argparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def init_whatsapp_profile(profile_dir):
    options = Options()
    # Do NOT use headless mode for logging in
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")
    options.add_argument(f"--user-data-dir={profile_dir}")

    driver = webdriver.Chrome(options=options)
    driver.get("https://web.whatsapp.com/")
    print("[INFO] WhatsApp Web loaded.")
    print("[ACTION] Please scan the QR code with your phone to log in.")
    print("[ACTION] After login, press ENTER here to close and save the profile.")
    input()
    driver.quit()
    print(f"[INFO] Profile initialized and saved to {profile_dir}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a Chrome profile for WhatsApp Web automation.")
    parser.add_argument("--profile_dir", required=True, help="Path to Chrome user profile directory to initialize/use.")
    args = parser.parse_args()
    init_whatsapp_profile(args.profile_dir)