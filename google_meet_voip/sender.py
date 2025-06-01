import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROFILE_DIR = "discord_voip/profiles/profileA"  # Update as needed
CHANNEL_URL = "https://discord.com/channels/1376607661830705293/1376607662518829189"  # Update as needed

def main():
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    driver = webdriver.Chrome(options=options)
    driver.get(CHANNEL_URL)
    wait = WebDriverWait(driver, 30)
    time.sleep(5)  # Let the page finish redirecting

    # Try multiple selectors for chatbox
    chatbox = None
    try:
        chatbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))
    except:
        try:
            chatbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-slate-editor='true']")))
        except:
            chatbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'slateTextArea-')]")))

    chatbox.click()
    chatbox.send_keys("Hello from sender!")
    chatbox.send_keys("\n")
    time.sleep(3)
    driver.quit()

if __name__ == "__main__":
    main()