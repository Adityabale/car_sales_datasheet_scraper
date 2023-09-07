import os
import warnings

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from zenke_scraper import ZenkeijikyoScraper


def main():
    CHROME_DRIVER = os.environ['CHROME_DRIVER_PATH']
    service = ChromeService(executable_path=CHROME_DRIVER)
    # chrome_options = ChromeOptions()
    driver = webdriver.Chrome(service=service)  # options=chrome_options)
    driver.maximize_window()

    warnings.simplefilter(action='ignore', category=FutureWarning)

    scraper = ZenkeijikyoScraper()
    scraper.driver = driver
    scraper.get_data_sheets_links()


if __name__ == '__main__':
    program_start = datetime.now()
    main()
    program_end = datetime.now()
    print(
        f'Total time taken to run all the scrapers from {program_start} to {program_end}'
        f' is {program_end - program_start}'
    )