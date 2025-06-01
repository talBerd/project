"""

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

def send_whatsapp_audio_with_capture(chat_name, audio_path, user_profile_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_output_dir = os.path.join(config["pcap_output_directory"], "voice", "whatsapp")
    os.makedirs(base_output_dir, exist_ok=True)

    base_filename = f"whatsapp-audio-[{timestamp}]"
    base_path = os.path.join(base_output_dir, base_filename)

    json_file = f"{base_path}.json"
    key_file = f"{base_path}.key"
    pcap_file = f"{base_path}.pcap"

    with open(key_file, 'a'):
        os.utime(key_file, None)

    options = Options()
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
    wait = WebDriverWait(driver, 180)
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

    # Click the attach (paperclip) button
    attach_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@title='Attach']"))
    )
    attach_btn.click()
    time.sleep(30)  # Let the UI open

    # Find the audio input and make sure it's visible
    #audio_inputs = driver.find_elements(By.XPATH, "//input[@accept='audio/*']")
    menu_buttons = driver.find_elements(By.XPATH, "//div[@role='menu']//button")
    for idx, btn in enumerate(menu_buttons):
        print(f"{idx}: {btn.get_attribute('outerHTML')}")
    audio_input = wait.until(
       EC.presence_of_element_located((By.XPATH, "//input[@accept='audio/*']"))
    )
    audio_input = None
    for inp in audio_inputs:
        if inp.is_displayed():
            audio_input = inp
            break
    if not audio_input:
        logger.error("Audio input field not found or not visible!")
        driver.quit()
        tshark.kill_tshark(tshark_process)
        return

    audio_abs_path = os.path.abspath(audio_path)
    if not os.path.exists(audio_abs_path):
        logger.error(f"Audio file not found: {audio_abs_path}")
        driver.quit()
        tshark.kill_tshark(tshark_process)
        return

    logger.info(f"[INFO] Attaching audio file: {audio_abs_path}")
    audio_input.send_keys(audio_abs_path)
    time.sleep(2)  # Let WhatsApp process the file

    # Wait for the send button to appear and click it
    try:
        send_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send']"))
        )
        logger.info("[INFO] Send button found, clicking...")
        send_btn.click()
        logger.info(f"[INFO] Audio sent to '{chat_name}' from file: {audio_path}")
    except Exception as e:
        logger.error(f"[ERROR] Send button not found or not clickable after file attach: {e}")
        driver.quit()
        tshark.kill_tshark(tshark_process)
        return

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
    parser = argparse.ArgumentParser(description="Send WhatsApp audio and capture traffic to pcap.")
    parser.add_argument("--profile_dir", required=True, help="Path to Chrome user profile directory")
    parser.add_argument("--chat_name", required=True, help="Name of the chat/contact to send audio to")
    parser.add_argument("--audio_path", required=True, help="Path to the audio file to send")
    args = parser.parse_args()
    send_whatsapp_audio_with_capture(args.chat_name, args.audio_path, args.profile_dir)

    """

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

def play_first_audio_with_capture(chat_name, user_profile_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    base_output_dir = os.path.join(config["pcap_output_directory"], "voip", "whatsapp")
    os.makedirs(base_output_dir, exist_ok=True)

    base_filename = f"whatsapp-[{timestamp}]"
    base_path = os.path.join(base_output_dir, base_filename)

    json_file = f"{base_path}.json"
    key_file = f"{base_path}.key"
    pcap_file = f"{base_path}.pcap"

    # Touch the key file to ensure it exists
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
    wait = WebDriverWait(driver, 30)
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

    # Wait for chat to load
    time.sleep(2)
    chat_panel = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'copyable-area')]"))
    )

    logger.info("[INFO] Scrolling chat to load messages...")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", chat_panel)
    time.sleep(1)

    logger.info("[INFO] Searching for audio messages...")
    # WhatsApp audio messages usually have a play button with data-icon="audio-play"
    audio_play_buttons = driver.find_elements(By.XPATH, "//button[@data-icon='audio-play'] | //span[@data-icon='audio-play']")
    if not audio_play_buttons:
        logger.error("No audio play buttons found! Try scrolling more or check the XPATH.")
    else:
        play_btn = audio_play_buttons[0]
        driver.execute_script("arguments[0].scrollIntoView(true);", play_btn)
        time.sleep(0.5)
        play_btn.click()
        logger.info("Played the first audio message in the chat.")
        logger.info(f"Waiting {config.get('audio_play_capture_time', 10)} seconds while capturing traffic...")
        time.sleep(config.get("audio_play_capture_time", 10))

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
    parser = argparse.ArgumentParser(description="Scroll WhatsApp chat, play first audio message and capture traffic to pcap.")
    parser.add_argument("--profile_dir", required=True, help="Path to Chrome user profile directory")
    parser.add_argument("--chat_name", required=True, help="Name of the chat/contact to operate on")
    args = parser.parse_args()
    play_first_audio_with_capture(args.chat_name, args.profile_dir)