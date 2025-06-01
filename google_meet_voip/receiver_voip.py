import time
import sys
import os
import argparse
import yaml
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import tshark

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


channel_url= "https://discord.com/channels/1376607661830705293/1376985306766639175"
user_profile= "discord_voip/profiles/profileA"

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)



def join_discord_with_capture(channel_url, user_profile_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_output_dir = os.path.join(config["pcap_output_directory"], "voip", "discord")
    os.makedirs(base_output_dir, exist_ok=True)

    base_filename = f"discord-[{timestamp}]"
    base_path = os.path.join(base_output_dir, base_filename)

    json_file = f"{base_path}.json"
    key_file = f"{base_path}.key"
    pcap_file = f"{base_path}.pcap"

    with open(key_file, 'a'):
        os.utime(key_file, None)

    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")
    options.add_argument(f"--user-data-dir={user_profile_dir}")
    options.add_argument(f"--log-net-log={json_file}")
    options.add_argument(f"--ssl-key-log-file={key_file}")

    logger.info("[INFO] Starting continuous tshark capture...")
    tshark_process = tshark.run_tshark(config["network_interface"], pcap_file)
    logger.info(f"[INFO] Waiting {config['warmup_time']}s for warmup...")
    time.sleep(config["warmup_time"])

    logger.info("[INFO] Launching Chrome...")
    driver = webdriver.Chrome(options=options)

    logger.info(f"[INFO] Navigating to: {channel_url}")
    driver.get(channel_url)

    logger.info("[INFO] Discord text channel loaded. Waiting for voice join button...")

    # Wait for and click the Join Voice button (by class containing 'joinButton')
    try:
        wait = WebDriverWait(driver, 30)
        join_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='joinButton']"))
        )
        join_button.click()
        logger.info("[INFO] Clicked the Join Voice button.")
    except Exception as e:
        logger.error(f"[ERROR] Could not find/click Join Voice button: {e}")

    logger.info("[INFO] Now connected to the voice channel.")

     # Try to unmute if muted on join
    # Discord may have "Unmute" or "Turn On Microphone" button, depending on UI language and state
    mute= True
    label = "Mute" if mute else "Unmute"
    try:
        wait = WebDriverWait(driver, 30)
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[aria-label='{label}']"))
        )
        button.click()
        logger.info(f"[INFO] Clicked the {label} button.")
    except Exception as e:
        logger.error(f"[ERROR] Could not find/click {label} button: {e}")


    try:
        print("\nPress ENTER to stop capture and close browser...")
        input()
        tshark.kill_tshark(tshark_process)
        logger.info(f"[INFO] Capture finished: {pcap_file}")
    except KeyboardInterrupt:
        logger.info("[INFO] Capture interrupted by user.")
        tshark.kill_tshark(tshark_process)

    time.sleep(2)
    driver.quit()
    logger.info("[INFO] Browser closed.")

if __name__ == "__main__":
    #parser = argparse.ArgumentParser()
    #args = parser.parse_args()

    join_discord_with_capture(channel_url, user_profile)