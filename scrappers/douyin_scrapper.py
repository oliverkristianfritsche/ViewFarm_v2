from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time

# Setup Firefox options
firefox_options = Options()
# Comment this out to run in non-headless mode
# firefox_options.add_argument("--headless")  
firefox_options.add_argument("--disable-gpu")
firefox_options.add_argument("--no-sandbox")

# Setup the WebDriver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)

# URL of the Douyin discover page
url = "https://www.douyin.com/discover"

# Load the page
driver.get(url)

# Introduce a delay to allow the page to load and CAPTCHA/manual intervention
time.sleep(5)  # Adjust this if necessary

# Close the pop-up if it appears
try:
    close_button = driver.find_element(By.CLASS_NAME, 'douyin-login__close')
    close_button.click()
    time.sleep(1)  # Give it a moment to close
except:
    print("Pop-up not found or already closed.")

# Find all video elements by class name
videos = driver.find_elements(By.CLASS_NAME, 'nFJH7DcV')

# Print their links
for video in videos:
    href = video.get_attribute('href')
    full_link = f"https:{href}" if href else 'None'  # Make the link absolute if needed
    print(full_link)

# Close the browser
driver.quit()
