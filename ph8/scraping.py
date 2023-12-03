from html2text import HTML2Text
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
import ph8.config

logger = logging.getLogger(__name__)


def create_chrome_options() -> Options:
    chrome_options = Options()

    # Disable sandbox if running as root (Docker)
    if ph8.config.chrome.disable_sandbox:
        logger.info("Running as root, adding --no-sandbox to chrome options")
        chrome_options.add_argument("--no-sandbox")

    # Set the user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"--user-agent={user_agent}")

    # Run headless
    chrome_options.add_argument("--headless")

    # Disable shared memory
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Disable the loading of images
    chrome_options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_settings.images": 2,
            "profile.managed_default_content_settings.images": 2,
        },
    )

    return chrome_options


def get_text_content_from_url(url):
    driver = webdriver.Chrome(options=create_chrome_options())
    driver.get(url)

    results = f"""<web-browser-results url="{url}">\n"""
    results += f"""<text-content>\n{driver.find_element(By.TAG_NAME, "body").text}</text-content>\n"""
    results += (
        "<links>\n"
        + "\n".join(
            [
                f"""  <link href="{l.get_attribute('href')}">{l.text}</link>"""
                for l in driver.find_elements(By.TAG_NAME, "a")
            ]
        )
        + "</links>\n"
    )
    results += "</web-browser-results>\n"

    driver.quit()

    return results


if __name__ == "__main__":
    text_content = get_text_content_from_url("https://scummy.dev")
    print(text_content)
