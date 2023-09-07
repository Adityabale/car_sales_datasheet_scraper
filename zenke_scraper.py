import time
import pandas as pd

from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class ZenkeijikyoScraper:
    """Gets the car sales data for light and small motor vehicles from zenkeijikyo website using
    selenium webdriver and panadas dataframe"""
    main_page = 'https://www.zenkeijikyo.or.jp/statistics'
    month_id_name = {
        '1': 'Jan', '2': 'Feb', '3': 'Mar', '4': 'Apr', '5': 'May', '6': 'Jun', '7': 'Jul',
        '8': 'Aug', '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
    }

    def __init__(self):
        """ Initialize the webdriver"""
        self.driver: Optional[WebDriver] = None
        self.session = None

    def get_data_sheets_links(self):
        """Gets the data sheets for every month from the available years for light and small
        motor vehicles."""
        actions = ActionChains(self.driver)
        wait5s = WebDriverWait(self.driver, 5)
        self.driver.get(self.main_page)
        car_sales_div = wait5s.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="sect en"] ~ div')))
        actions.scroll_to_element(car_sales_div).perform()
        wait5s.until(EC.visibility_of(car_sales_div))
        sales_links = car_sales_div.find_elements(By.TAG_NAME, 'a')[:2]
        for idx, link in enumerate(sales_links):
            car_sales_div = wait5s.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="sect en"] ~ div')))
            sales_links = car_sales_div.find_elements(By.TAG_NAME, 'a')[:2]
            sales_data_type = car_sales_div.find_elements(By.TAG_NAME, 'h5')[idx].get_attribute('innerText').strip()
            wait5s.until(EC.element_to_be_clickable(sales_links[idx])).click()
            year_sections = wait5s.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="section year"]')))
            for i, year_section in enumerate(year_sections):
                year_sections = wait5s.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="section year"]')))
                actions.scroll_to_element(year_sections[i]).perform()
                wait5s.until(EC.visibility_of(year_sections[i]))
                year = year_sections[i].find_element(By.TAG_NAME, 'h2').get_attribute('innerText').strip()
                monthly_stats_elms = year_sections[i].find_elements(By.CSS_SELECTOR, 'h2 ~ ul > li[class^="stat"] a')
                if not monthly_stats_elms:
                    monthly_stats_elms = year_sections[i].find_elements(By.CSS_SELECTOR, 'h2 ~ ul > li a')
                for num, stats_link_elm in enumerate(monthly_stats_elms):
                    year_sections = wait5s.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="section year"]')))
                    monthly_stats_elms = year_sections[i].find_elements(By.CSS_SELECTOR, 'h2 ~ ul > li[class^="stat"] a')
                    if not monthly_stats_elms:
                        monthly_stats_elms = year_sections[i].find_elements(By.CSS_SELECTOR, 'h2 ~ ul > li a')
                    link = monthly_stats_elms[num].get_attribute('href')
                    month_id = monthly_stats_elms[num].get_attribute('innerText').strip()
                    self._get_table_data(link, sales_data_type, month_id, year)
                    self.driver.back()
            self.driver.back()

    def _get_table_data(self, url: str, data_type: str, month_id: str, year: str):
        """Uses webdriver to open the table link, uses pandas to parse the html, gets the table 
        data using pandas DataFrame and writes the same into a csv file."""
        self.driver.get(url)
        time.sleep(1)
        try:
            tables = pd.read_html(self.driver.page_source)
            df = pd.DataFrame(tables[0])
            if df.iloc[0:1, 1].isnull()[0]:
                try:
                    df = df.dropna(subset=4)
                except KeyError:
                    pass
            try:
                month = self.month_id_name[month_id]
            except KeyError:
                try:
                    month_id = month_id.replace(month_id[-1], '').strip()
                    month = self.month_id_name[month_id]
                except KeyError:
                    month = ''
            if month:
                folder_path = Path(f'scraped_data/{data_type}')
                if not folder_path.exists():
                    folder_path.mkdir()
                if isinstance(list(df.columns)[0], int):
                    df.to_csv(Path(f'scraped_data/{data_type}/{month}_{year}_{data_type}.csv'), 
                              encoding='utf-8', index=False, header=False)
                else:
                    df.to_csv(Path(f'scraped_data/{data_type}/{month}_{year}_{data_type}.csv'), 
                              encoding='utf-8', index=False)
                print(f"Saved file: {month}_{year}_{data_type}.csv")
                
        except ValueError:
            pass



