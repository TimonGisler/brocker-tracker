import os
import re
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver


# File into which the scraped data will be saved
FILE_PATH = "data/data.txt"

URLS_TO_SCRAPE = [ "https://www.home.saxo/en-mena/legal/risk-warning/saxo-risk-warning"
               , "https://www.interactivebrokers.co.uk/de/index.php?f=38931&cc=US"
               , "https://www.etoro.com/trading/cfd-leverage-and-margin/"
               , "https://www.ig.com/en/risk-management/what-is-leverage"
               , "https://www.icmarkets.eu/en/education/advantages-of-cfds"
               , "https://helpcentre.trading212.com/hc/en-us"
               , "https://www.plus500.com/en-es/"
               , "https://capital.com/"
               , "https://www.xtb.com/en/education/what-is-cfd-trading"]


def save_data_to_file(percentage_which_loose_money, broker_url):
    """Saves the scraped data to the file defined in FILE_PATH."""
    print("Percentage:", percentage_which_loose_money)

    # Open the file in append mode
    with open(FILE_PATH, "a", encoding="utf-8") as file_to_write_percentage_down:
        # Append the data to the file
        file_to_write_percentage_down.write(broker_url + ": " + percentage_which_loose_money + "\n")

    print("Data appended to the file successfully.")


def scrape_site_for_cfd_text(url_to_scrape):
    """scrapes the passed site for the percentage of retail investors that loose money with CFDs and saves it to a file."""
    # Set up the browser
    # user agent string must be set to avoid detection by the website (that we run headless mode --> captcha))
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = webdriver.ChromeOptions()
    # specify headless mode
    options.add_argument('--headless=new')
    # specify the desired user agent
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    # Load the website and get the page source and then the text
    driver.get(url_to_scrape)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    text = soup.get_text()
    driver.quit()

    # Search for the specific text pattern
    pattern = r"(\d+.?\d+)% of retail"
    match = re.search(pattern, text)
    percentage = match.group(1) # TODO TGIS, make sure that if this does not work, the program does not crash and some default value is used as percentage

    # Save the percentage
    save_data_to_file(percentage, url_to_scrape)



# Ensure the directory exists
os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

# add current date to file
with open(FILE_PATH, "a", encoding="utf-8") as file:
    file.write("\n" + "Date: " + date.today().strftime('%Y-%m-%d') + "\n")

# Loop through the urls and scrape the text
for url in URLS_TO_SCRAPE:
    scrape_site_for_cfd_text(url)
