import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyttsx3

PROFILE_DIR = "discord_voip/profiles/profileB"
VOICE_CHANNEL_URL = "https://discord.com/channels/1376607661830705293/1376985306766639175"
WAV_FILE = "sample.wav"  # Must be 16-bit 48kHz mono PCM


def main():
    engine = pyttsx3.init()
    engine.save_to_file('This is a test for Discord.', 'sample.wav')
    engine.runAndWait()
    print("Audio file 'sample.wav' created.")

    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--use-fake-device-for-media-stream")
    options.add_argument(f"--use-file-for-fake-audio-capture={WAV_FILE}")
    driver = webdriver.Chrome(options=options)
    driver.get(VOICE_CHANNEL_URL)
    time.sleep(7)  # Wait for page to load

    
    try:
        join_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='joinButton']"))
        )
        join_button.click()
        print("Clicked Join Voice button by partial class.")
    except Exception as e:
        print("Could not find/click Join Voice button by partial class:", e)
        # Wait a bit to ensure voice session is set up
        time.sleep(3)

     # Try to unmute if muted on join
    # Discord may have "Unmute" or "Turn On Microphone" button, depending on UI language and state
    mute= True
    label = "Mute" if mute else "Unmute"
    try:
        # Assuming 'driver' is your webdriver.Chrome instance
        wait = WebDriverWait(driver, 30)
        button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[aria-label='{label}']"))
        )
        button.click()
        print(f"[INFO] Clicked the {label} button.")
    except Exception as e:
        print(f"[ERROR] Could not find/click {label} button: {e}")

    # Stay in channel for a while to transmit audio
    time.sleep(20)

    driver.quit()

if __name__ == "__main__":
    main()