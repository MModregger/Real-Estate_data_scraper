# Real-Estate_data_scraper
Real-Estate_data_scraper is a project that uses Python to scrape data from a popular Italian Real Estate marketplace and create a dashboard to visualize the data.


# Objective
The main goal of this project is to access data that would otherwise require paying an API service, in order to get a glimpse of how the real estate market in a certain area is behaving. 

# Data Scraping
The code scraps the data directly from Immobiliare.it, it asks the user to input the name of a city and then proceeds to scrap and save the data from rent and sale ads. The data is then saved in an excel file, used datasource for the dashboard, as well as a supporting document for the user to go through the data.
The data collected is supposed to be a relevant driver for the price of rent/sale and is the following:
1. Rent or sale price of the property 
2. Size of the property
3. Address and district
4. Presence of Balcony/Terrace
5. Presence of a private parking spot/garage
6. Energy consumption
7. Energy class
8. Link to the ad 
 
# Dashboard
The Dashboard has the function of giving an immediate representation of the data. 
The price data is aggregated by district, the code calculates the average rent price per square meter and the average sale price per sqaure meter, as well as the average yearly yield.

# Control
The data scraping code uses certain HTML classes to extract the data from the website. Where possible I tried to avoid this method and program the code to extract the data through pattern recognition because the name opf the classes might change with time. To check whether the classes that are being used by the data scraping code are still actual I wrote a script that goes through the Immobiliare.it website and checks whether the classes used still exist. The only input the code needs is an example of sale/rent ad.

