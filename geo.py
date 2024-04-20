import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def generate_nickname(length=10):
    # 生成一个随机昵称，长度默认为10
    letters = string.ascii_letters
    nickname = ''.join(random.choice(letters) for i in range(length))
    print("nickname:", nickname)
    return nickname


def automate_website(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
    chrome_options.add_argument("--disable-extensions")  # 禁用扩展
    chrome_options.add_argument("start-maximized")  # 最大化运行
    chrome_options.add_argument("disable-infobars")  # 禁用浏览器正在被自动化程序控制的提示
    chrome_options.add_argument("--disable-images")  # 禁用图片加载
    chrome_options.page_load_strategy = 'none'  # 不等待完全加载（注意：这可能影响脚本稳定性）


    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 60)  # 设置最长等待时间为10秒

    try:
        driver.get(url)

        nickname_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'text-input_textInput__')][@name='nick']"))
        )
        nickname = generate_nickname()
        nickname_input.send_keys(nickname)

        # 点击"Play as guest"按钮
        play_guest_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'button_label__') and contains(text(), 'Play as guest')]"))
        )
        driver.execute_script("arguments[0].click();", play_guest_button)

        # # 等待并找到动态类名的div元素，使用JavaScript进行点击
        # canvas_container = wait.until(
        #     EC.presence_of_element_located((By.XPATH, "//div[starts-with(@class, 'guess-map_canvasContainer__')]"))
        # )
        # driver.execute_script("arguments[0].click();", canvas_container)

        # 等待并找到画布容器
        print("Clicking the map point...")
        time.sleep(10)
        canvas_container = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-qa='guess-map-canvas']"))
        )
        time.sleep(20)
        actions.move_to_element(canvas_container).click(canvas_container).perform()

        # 等待并找到"GUESS"按钮，使用JavaScript进行点击
        print("Clicking the guess button...")
        guess_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-qa='perform-guess'][@type='button']"))
        )
        driver.execute_script("arguments[0].click();", guess_button)

        # 等待并找到<img alt="Correct location">的元素，使用JavaScript进行点击
        print("Finding the correct location image...")
        correct_location_image = wait.until(
            EC.presence_of_element_located((By.XPATH, "//img[@alt='Correct location']"))
        )
        driver.execute_script("arguments[0].click();", correct_location_image)

        # 这里假设新网址在跳转或新标签中打开
        # 获取当前所有打开的窗口句柄
        windows = driver.window_handles
        if len(windows) > 1:
            # 切换到新打开的窗口
            driver.switch_to.window(windows[-1])

        # 返回新页面的网址
        return driver.current_url

    finally:
        driver.quit()

# 使用函数
url = "https://www.geoguessr.com/challenge/j5QTVixXslrbDXHj"  # 替换为你需要操作的网址
new_url = automate_website(url)
print("New URL:", new_url)
