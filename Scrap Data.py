#!/usr/bin/env python
# coding: utf-8


# Scrap data from Immobiliare.it and save it to excel file


# In[1]:


import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import re

def process_ads_on_current_page(driver, dataset, query):
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "nd-mediaObject")))
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    ads = soup.find_all("div", class_="nd-mediaObject__content")

    for ad in ads:
        try:
            title_element = ad.find("a", class_="in-listingCardTitle")
            ad_link = title_element["href"] if title_element else ""

            if ad_link:
                driver.execute_script("window.open('" + ad_link + "', 'new_window')")
                driver.switch_to.window(driver.window_handles[1])
                
                start_time = time.time()
                loaded = False

                while not loaded and (time.time() - start_time) < 10:
                    try:
                        ad_html = driver.page_source
                        ad_soup = BeautifulSoup(ad_html, "html.parser")
                        address_element = ad_soup.find("h1", class_="re-title__title")
                        if address_element:
                            loaded = True
                        else:
                            time.sleep(0.5)
                    except Exception:
                        driver.refresh()
                        time.sleep(2)

                if not loaded:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                address_element = ad_soup.find("h1", class_="re-title__title")
                address = "N/A"
                district = "N/A"
                if address_element:
                    address_text = address_element.get_text(strip=True)

                    address_parts = address_text.split(',')
                    if len(address_parts) >= 2:
                        address = address_parts[0].strip()
                        district = address_parts[1].strip()

                        if any(keyword in district.lower() for keyword in ["piano", "piani", "stato", "m²"]):
                            if len(address_parts) > 2:
                                district = address_parts[2].strip()
                        elif district.isdigit():
                            if len(address_parts) > 2:
                                district = address_parts[2].strip()

                prezzo_su_richiesta_element = ad_soup.find(string="Prezzo su richiesta")
                if prezzo_su_richiesta_element:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                price_elements = ad_soup.find_all(string=re.compile(r'€\s?\d+(?:[\.,]\d+)*'))
                price = "N/A"
                if price_elements:
                    for price_text in price_elements:
                        price_text = price_text.strip()
                        if re.match(r'€\s?\d+(?:[\.,]\d+)*', price_text):
                            if '-' in price_text:
                                price = "N/A"
                                break
                            else:
                                price = price_text.replace("€", "").replace(".", "").replace(",", ".").strip()
                                try:
                                    price = float(re.sub(r'[^\d.]', '', price))
                                except ValueError:
                                    price = "N/A"
                                break

                if price == "N/A":
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                area_element = ad_soup.find(string=re.compile(r'\d+\s?m²'))
                area = "N/A"
                if area_element:
                    area_text = area_element.strip()
                    if re.match(r'\d+\s?m²', area_text):
                        area = area_text.replace("m²", "").strip()
                        try:
                            area = float(area)
                        except ValueError:
                            area = "N/A"

                energy_consumption_element = ad_soup.find(string=re.compile(r'\d+(\.\d+)?\s?kWh/m²\s?anno'))
                energy_consumption = "N/A"
                energy_class = "N/A"
                if energy_consumption_element:
                    energy_consumption = energy_consumption_element.strip()
                    following_text = energy_consumption_element.find_next(string=True).strip()
                    energy_classes = ["A4", "A3", "A2", "A1", "A+", "A", "B", "C", "D", "E", "F", "G"]
                    for energy_class_candidate in energy_classes:
                        if energy_class_candidate in following_text:
                            energy_class = energy_class_candidate
                            break

                parking_element = ad_soup.find(string=re.compile(r'in box privato/box in garage|in parcheggio/garage comune', re.IGNORECASE))
                parking = "Yes" if parking_element else "No"

                balcony_terrace_element = ad_soup.find(string=re.compile(r'Balcone|Terrazzo', re.IGNORECASE))
                balcony_terrace = "Yes" if balcony_terrace_element else "No"

                price_per_sqm = "N/A"
                if price != "N/A" and area != "N/A":
                    try:
                        price_per_sqm = price / area
                    except (TypeError, ValueError):
                        price_per_sqm = "N/A"

                if price_per_sqm == "N/A":
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                ad_id = (address + str(area)).replace(" ", "")

                dataset.append({
                    "ID": ad_id,
                    "Address": address,
                    "District": district,
                    "Price": price,
                    "Area": area,
                    "Price per Square Meter": price_per_sqm,
                    "Parking": parking,
                    "Balcony/Terrace": balcony_terrace,
                    "Energy Consumption": energy_consumption,
                    "Energy Class": energy_class,
                    "Link": ad_link
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing ad: {e}")

def navigate_to_next_page(driver):
    try:
        next_button = driver.find_element(By.XPATH, "//a[@class='in-pagination__item nd-button nd-button--ghost' and .//span[text()='Successiva']]")
        next_url = next_button.get_attribute("href")
        driver.get(next_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "nd-mediaObject")))
        return True
    except NoSuchElementException:
        print("Next button not found. End of pagination.")
        return False

def clear_search_bar(driver):
    """Helper function to clear the search bar manually."""
    search_input = driver.find_element(By.CSS_SELECTOR, ".hp-searchForm__item.hp-searchForm__item--location input")
    search_input.click()  # Focus on the search bar
    search_input.send_keys(Keys.CONTROL + "a")  # Select all text (works on Windows, use Command + "a" for Mac)
    time.sleep(0.5)  # Short delay to ensure the selection is registered
    search_input.send_keys(Keys.BACKSPACE)  # Delete the selected text
    time.sleep(0.5)  # Short delay to ensure the deletion is processed

def search_on_immobiliare(query):
    dataset_rent = []
    dataset_sale = []

    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://www.immobiliare.it/")
        affitta_button = driver.find_element(By.XPATH, "//button[@id='rent-tab']")
        affitta_button.click()
        clear_search_bar(driver)
        search_input = driver.find_element(By.CSS_SELECTOR, ".hp-searchForm__item.hp-searchForm__item--location input")
        search_input.send_keys(query)
        time.sleep(1)
        search_input.send_keys(Keys.RETURN)
        time.sleep(1)
        search_button = driver.find_element(By.CSS_SELECTOR, ".hp-searchForm__button")
        search_button.click()
        time.sleep(2)

        while True:
            process_ads_on_current_page(driver, dataset_rent, query)
            if not navigate_to_next_page(driver):
                break

        driver.get("https://www.immobiliare.it/")
        vendita_button = driver.find_element(By.XPATH, "//button[@id='sale-tab']")
        vendita_button.click()
        clear_search_bar(driver)
        search_input = driver.find_element(By.CSS_SELECTOR, ".hp-searchForm__item.hp-searchForm__item--location input")
        search_input.send_keys(query)
        time.sleep(1)
        search_input.send_keys(Keys.RETURN)
        time.sleep(1)
        search_button = driver.find_element(By.CSS_SELECTOR, ".hp-searchForm__button")
        search_button.click()
        time.sleep(2)

        while True:
            process_ads_on_current_page(driver, dataset_sale, query)
            if not navigate_to_next_page(driver):
                break

    finally:
        driver.quit()

    df_rent = pd.DataFrame(dataset_rent)
    df_sale = pd.DataFrame(dataset_sale)
    df_rent = df_rent.replace("N/A", pd.NA).dropna(how='all')
    df_sale = df_sale.replace("N/A", pd.NA).dropna(how='all')

    excel_path = "/Users/michelemodregger/Desktop/varie/Real Estate/real_estate_data.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        df_rent.to_excel(writer, sheet_name='Rent Data', index=False)
        df_sale.to_excel(writer, sheet_name='Sale Data', index=False)

    return df_rent, df_sale

if __name__ == "__main__":
    query = input("Enter your search query: ")
    search_on_immobiliare(query)


