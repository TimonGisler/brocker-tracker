# pylint: disable=line-too-long
import os
import re
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib

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
               , "https://www.xtb.com/en/education/what-is-cfd-trading"
               ]


def main():
    """Main function of the program."""
    # Set up the file
    set_up_file()

    # Loop through the urls and scrape the text
    for url in URLS_TO_SCRAPE:
        try:
            text = get_page_text_using_selenium(url)
            percentage = extract_percentage_from_text(text)
            save_data_to_file(percentage, url)
        # pylint: disable-next=W0718
        except Exception as e:
            print("Error: ", e)
            save_data_to_file("Error: " +  repr(e), url)
            send_mail_with_data()


def set_up_file():
    """Sets up the file to which the scraped data will be saved. (add current date and create file if it does not exist)"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

    # add current date to file
    with open(FILE_PATH, "a", encoding="utf-8") as file:
        file.write("\n" + "Date: " + date.today().strftime('%Y-%m-%d') + "\n")


def get_page_text_using_selenium(url_to_scrape):
    """Gets the text of the page at the passed URL."""

    # Set up the browser
    # user agent string must be set to avoid detection by the website (that we run headless mode --> captcha))
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = webdriver.ChromeOptions()
    # specify headless mode
    options.add_argument('--headless=new')
    # specify the desired user agent
    options.add_argument(f'user-agent={user_agent}')

    # https://stackoverflow.com/a/53970825/15015069 --> prevent crashing on certain websites
    options.add_argument('--disable-dev-shm-usage')

    # guide to run selenium in container and connect: (https://stackoverflow.com/questions/45323271/how-to-run-selenium-with-chrome-in-docker)
    #local dev commands/code (with docker):
    # docker run -d -p 4444:4444 selenium/standalone-chrome
    # driver = driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME, options=options)
    # driver = driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
    # local dev (withoud docker):
    driver = webdriver.Chrome(options=options)


    # Load the website and get the page source and then the text
    driver.get(url_to_scrape)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    text = soup.get_text()
    driver.quit()
    return text


def extract_percentage_from_text(text):
    """Extracts the percentage of retail investors that loose money from the passed text."""
    # Search for the specific text pattern
    pattern = r"(\d+.?\d+)% of retail"
    match = re.search(pattern, text)
    percentage = match.group(1)
    return percentage


def save_data_to_file(percentage_which_loose_money, broker_url):
    """Saves the scraped data to the file defined in FILE_PATH."""
    print("Percentage:", percentage_which_loose_money)

    # Open the file in append mode
    with open(FILE_PATH, "a", encoding="utf-8") as file_to_write_percentage_down:
        # Append the data to the file
        file_to_write_percentage_down.write(broker_url + ": " + percentage_which_loose_money + "\n")

    print("Data appended to the file successfully.")



def send_mail_with_data():
    """Sends an email with the scraped data.
    Make sure the env variableEMAIL_PASSWORD are set."""
    # send mail with gmail
    FROM = "devtestaccpersonal@gmail.com"
    PW = "INSERT APP PW HERE"
    TO = "timongisler@icloud.com"
    SUBJECT = "Gambling brocker tracker"
    TEXT = "TEST TEXT, does it work? TODO: add scraped data to the mail."

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(FROM, PW)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except Exception as e:
        print("failed to send mail: ", e)


# Run the main function
if __name__ == "__main__":
    print("Starting the program...")
    main()
