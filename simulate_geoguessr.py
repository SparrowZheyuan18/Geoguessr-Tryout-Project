import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def generate_nickname(length=10):
    # Generate a random nickname
    letters = string.ascii_letters
    nickname = ''.join(random.choice(letters) for i in range(length))
    print("nickname:", nickname)
    return nickname


def one_round_game(driver, wait, actions):
    print("Loading...")

    time.sleep(10)  # For stablitity
    # Wait and find the canvas container, then move and click it
    canvas_container = wait.until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-qa='guess-map-canvas']"))
    )
    time.sleep(10) # For stablitity
    actions.move_to_element(canvas_container).click(canvas_container).perform()

    # Find the Guess button and click it
    print("Clicking the guess button...")
    guess_button = wait.until(
        EC.presence_of_element_located((By.XPATH, "//button[@data-qa='perform-guess'][@type='button']"))
    )
    driver.execute_script("arguments[0].click();", guess_button)

    # Find the correct location spot and click it
    print("Finding the correct location image...")
    correct_location_image = wait.until(
        EC.presence_of_element_located((By.XPATH, "//img[@alt='Correct location']"))
    )
    driver.execute_script("arguments[0].click();", correct_location_image)

    # Get the new URL in the new window
    windows = driver.window_handles
    if len(windows) > 1:
        driver.switch_to.window(windows[-1])

    url = driver.current_url
    driver.close()
    driver.switch_to.window(windows[0])
    return url


def automate_website(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # headless mode
    chrome_options.add_argument("--disable-extensions") 
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-images") 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 60)  # 60 seconds waiting time

    urls = []

    try:
        driver.get(url)

        nickname_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'text-input_textInput__')][@name='nick']"))
        )
        nickname = generate_nickname()
        nickname_input.send_keys(nickname)

        # Click the Play as guest button
        play_guest_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'button_label__') and contains(text(), 'Play as guest')]"))
        )
        driver.execute_script("arguments[0].click();", play_guest_button)

        for i in range(5):
            print(f"Round {i+1}")
            url = one_round_game(driver, wait, actions)
            urls.append(url)
            if i != 4:
                # Click the Next button to 
                print("Clicking the Next button...")
                next_round_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'button_label__') and contains(text(), 'Next')]"))
                )
                driver.execute_script("arguments[0].click();", next_round_button)
        
        return urls

    finally:
        driver.quit()


starttime = time.time()
print("Start simulating the website...")
url = "https://www.geoguessr.com/challenge/j5QTVixXslrbDXHj"
new_url = automate_website(url)
print("New URL:", new_url)
endtime = time.time()
print("Time used:", endtime - starttime)
