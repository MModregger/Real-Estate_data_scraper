#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# check whether the used classes are still actual


# In[ ]:


import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from tabulate import tabulate

def check_html_elements(driver, locators):
    results = {}
    for locator_name, locator in locators.items():
        try:
            driver.find_element(*locator)
            results[locator_name] = "Exists"
        except NoSuchElementException:
            results[locator_name] = "Does not exist"
    return results

def check_ad_detail_page(driver, ad_url):
    driver.get(ad_url)
    time.sleep(2)  # Wait for the ad page to load

    ad_detail_locators = {
        "Ad Address": (By.CLASS_NAME, "re-title__title")
    }

    return check_html_elements(driver, ad_detail_locators)

def print_results(title, results):
    print(f"\n{title}:")
    table = [(key, value) for key, value in results.items()]
    print(tabulate(table, headers=["Class/Element", "Status"], tablefmt="grid"))

if __name__ == "__main__":
    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Define locators for different pages
        home_page_locators = {
            "Search Bar": (By.CSS_SELECTOR, ".hp-searchForm__item.hp-searchForm__item--location input"),
            "Search Button": (By.CSS_SELECTOR, ".hp-searchForm__button")
        }

        ad_page_locators = {
            "General Ad Element": (By.CLASS_NAME, "nd-mediaObject"),
            "Ad Content": (By.CLASS_NAME, "nd-mediaObject__content"),
            "Ad Title": (By.CLASS_NAME, "in-listingCardTitle"),
            "Next Button": (By.XPATH, "//a[@class='in-pagination__item nd-button nd-button--ghost' and .//span[text()='Successiva']]")
        }

        # Check home page
        driver.get("https://www.immobiliare.it")
        home_results = check_html_elements(driver, home_page_locators)
        print_results("Home Page Results", home_results)

        # Check sale ad page
        driver.get("https://www.immobiliare.it/vendita-case/bergamo/")
        sale_results = check_html_elements(driver, ad_page_locators)
        print_results("Sale Ad Page Results", sale_results)

        # Check rent ad page
        driver.get("https://www.immobiliare.it/affitto-case/bergamo/")
        rent_results = check_html_elements(driver, ad_page_locators)
        print_results("Rent Ad Page Results", rent_results)

        # Ask user for a specific ad URL
        ad_url = input("Enter the URL of a specific ad to check the detail page: ")
        ad_detail_results = check_ad_detail_page(driver, ad_url)
        print_results("Ad Detail Page Results", ad_detail_results)

    finally:
        # Close the webdriver
        driver.quit()
