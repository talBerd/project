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

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def send_whatsapp_with_capture(chat_name, message, user_profile_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_output_dir = os.path.join(config["pcap_output_directory"], "chat", "whatsapp")
    os.makedirs(base_output_dir, exist_ok=True)

    base_filename = f"whatsapp-[{timestamp}]"
    base_path = os.path.join(base_output_dir, base_filename)

    json_file = f"{base_path}.json"
    key_file = f"{base_path}.key"
    pcap_file = f"{base_path}.pcap"

    with open(key_file, 'a'):
        os.utime(key_file, None)

    options = Options()
    # options.add_argument("--headless") # WhatsApp Web doesn't like headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,720")
    options.add_argument(f"--user-data-dir={user_profile_dir}")
    options.binary_location = "/usr/bin/chromium-browser"  # Change if necessary
    options.add_argument(f"--log-net-log={json_file}")
    options.add_argument(f"--ssl-key-log-file={key_file}")

    logger.info("[INFO] Starting continuous tshark capture...")
    tshark_process = tshark.run_tshark(config["network_interface"], pcap_file)
    logger.info(f"[INFO] Waiting {config['warmup_time']}s for warmup...")
    time.sleep(config["warmup_time"])

    logger.info("[INFO] Launching Chrome...")
    driver = webdriver.Chrome(options=options)

    logger.info("[INFO] Navigating to WhatsApp Web...")
    driver.get("https://web.whatsapp.com/")
    wait = WebDriverWait(driver, 60)
    search_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
    )

    search_box.clear()
    search_box.send_keys(chat_name)
    time.sleep(2)
    chat = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//span[@title='{chat_name}']"))
    )
    chat.click()
    msg_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
    )
    msg_box.send_keys(message)
    send_btn = driver.find_element(By.XPATH, "//span[@data-icon='send']")
    send_btn.click()
    logger.info(f"[INFO] Message sent to '{chat_name}': {message}")

    print("\n[INFO] Press ENTER to stop capture and close browser...")
    try:
        input()
    except KeyboardInterrupt:
        logger.info("[INFO] Capture interrupted by user.")

    tshark.kill_tshark(tshark_process)
    logger.info(f"[INFO] Capture finished: {pcap_file}")

    time.sleep(2)
    driver.quit()
    logger.info("[INFO] Browser closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send WhatsApp message and capture traffic to pcap.")
    parser.add_argument("--profile_dir", required=True, help="Path to Chrome user profile directory")
    parser.add_argument("--chat_name", required=True, help="Name of the chat/contact to send message to")
    parser.add_argument("--message", required=True, help="Message to send")
    args = parser.parse_args()
    send_whatsapp_with_capture(args.chat_name, args.message, args.profile_dir)