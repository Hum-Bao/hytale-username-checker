import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
PATH_CHROMEDRIVER = os.getenv("PATH_CHROMEDRIVER")
PATH_USERDATA_1 = os.getenv("PATH_USERDATA_1")
PATH_USERDATA_2 = os.getenv("PATH_USERDATA_2")
USERNAME = os.getenv("HYTALE_USERNAME")
PASSWORD = os.getenv("HYTALE_PASSWORD")


def load_file(file_name: str) -> list[str]:
    with Path(file_name).open() as f:
        return f.read().splitlines()


def create_browser(userdata_path: str) -> webdriver.Chrome:
    """Create a browser instance with specific user data directory."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=" + userdata_path)
    chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        service=Service(PATH_CHROMEDRIVER),
        options=chrome_options,
    )
    driver.get(
        ("https://accounts.hytale.com/reserve?token=" + os.getenv("HYTALE_TOKEN")),
    )
    time.sleep(5)
    return driver


def login(driver: webdriver.Chrome) -> None:
    try:
        element = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/astro-island/form/div[1]/div/button",
        )
        element.click()
    except:
        print("Can't login")
        return

    time.sleep(2)
    element = driver.find_element(By.ID, "identifier")
    element.send_keys(USERNAME)
    time.sleep(2)

    element = driver.find_element(By.ID, "password")
    element.send_keys(PASSWORD)
    time.sleep(2)

    element = driver.find_element(By.NAME, "method")
    element.click()
    time.sleep(5)


def check_names(
    driver: webdriver.Chrome,
    word_list: list[str],
    browser_id: int,
    file_name: str,
) -> None:
    element = driver.find_element(By.ID, "reserve-username")
    element.click()
    time.sleep(2)

    count = 0
    with Path(file_name).open("a") as output_file:
        while count < len(word_list):
            username = word_list[count]
            element.send_keys(username)

            wait = WebDriverWait(driver, 10)

            try:
                svg_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "svg.text-red-500, svg.text-green-600"),
                    ),
                )

                svg_class = svg_element.get_attribute("class")

                if "text-red-500" in svg_class:
                    print(f"[Browser {browser_id}] Unavailable: {username} (#{count})")
                elif "text-green-600" in svg_class:
                    print(f"[Browser {browser_id}] ✓ AVAILABLE: {username} (#{count})")
                    output_file.write(username + "\n")
                    output_file.flush()
                    os.fsync(output_file.fileno())
                else:
                    print(
                        f"[Browser {browser_id}] Unknown state: {username} (#{count})",
                    )

            except Exception as e:
                print(f"[Browser {browser_id}] Error checking {username}: {count}: {e}")

            count += 1
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)


def run_browser(
    browser_id: int,
    word_list: list[str],
    userdata_path: str,
    file_name: str,
) -> None:
    print(f"[Browser {browser_id}] Starting: checking {len(word_list)} words")
    driver = create_browser(userdata_path)
    login(driver)
    check_names(driver, word_list, browser_id, file_name)
    print(f"[Browser {browser_id}] Completed!")


def main(
    input_wordlist: str,
    output_file1: str,
    output_file2: str,
) -> None:
    word_list = load_file(input_wordlist)
    total_words = len(word_list)
    midpoint = total_words // 2

    print(f"Input wordlist: {input_wordlist}")
    print(f"Total words: {total_words}")
    print(f"Browser 1 will check: 0 to {midpoint} -> {output_file1}")
    print(f"Browser 2 will check: {midpoint} to {total_words} -> {output_file2}")

    # Create two threads for parallel execution
    # Use 2 output files because I don't want to sync writes to the same file. I'm lazy
    thread1 = threading.Thread(
        target=run_browser,
        args=(1, word_list[0:midpoint], PATH_USERDATA_1, output_file1),
    )
    thread2 = threading.Thread(
        target=run_browser,
        args=(2, word_list[midpoint:total_words], PATH_USERDATA_2, output_file2),
    )

    # Start both browsers
    thread1.start()
    thread2.start()

    # Wait for both to complete
    thread1.join()
    thread2.join()

    print("\nAll browsers completed!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python main.py <input_wordlist> <output_file1> <output_file2>")
        print(
            "Example: python main.py 3-letter-words.txt foundwords.txt foundwords2.txt",
        )
        sys.exit(1)

    input_wordlist = sys.argv[1]
    output_file1 = sys.argv[2]
    output_file2 = sys.argv[3]

    main(input_wordlist, output_file1, output_file2)
