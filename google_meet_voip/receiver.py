import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

user_profile = "discord_voip/profiles/profileB"  # Path to receiver's Chrome profile
channel_url = "https://discord.com/channels/1376607661830705293/1376607662518829189"  # Replace with your channel link

import time
import sys
import os
import argparse
import yaml
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import tshark

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def join_discord_with_capture(channel_url, user_profile_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_output_dir = os.path.join(config["pcap_output_directory"], "chat", "discord")
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

    logger.info("[INFO] Discord text channel loaded. Automation can interact with chat now.")

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
    join_discord_with_capture(channel_url, user_profile)