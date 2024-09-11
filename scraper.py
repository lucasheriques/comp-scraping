import time
import random
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fetch_page(driver, url, is_first_page=False):
    logging.info(f"Fetching page: {url}")
    driver.get(url)
    try:
        # Wait for the table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        logging.info(f"Table element found on the page")

        # Wait for the rows to be present (adjust the selector as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        logging.info(f"Table rows found on the page")

        if is_first_page:
            input("Press Enter after manually inspecting and scrolling the page...")

        # Give a short time for any dynamic content to load
        time.sleep(2)

    except Exception as e:
        logging.error(f"Error loading page {url}: {e}")

    return driver.page_source

def parse_salary_data(html):
    logging.info("Parsing salary data")
    data = []
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select_one('table')
    if not table:
        logging.error("No table found on the page")
        return data

    rows = table.select('tbody tr')
    logging.info(f"Found {len(rows)} rows in the table")

    for index, row in enumerate(rows, start=1):
        # Skip promotional rows
        if 'promo' in row.get('class', []):
            continue

        cols = row.select('td')
        if len(cols) == 4:
            company_cell = cols[0]
            level_cell = cols[1].select_one('p')
            role_cell = cols[1].select_one('span')
            yoe_cell = cols[2].select_one('p')
            yoe_company_cell = cols[2].select_one('span')
            total_comp_cell = cols[3].select_one('p')
            comp_breakdown_cell = cols[3].select_one('span')

            company_name = company_cell.select_one('a.salary-row_companyName__obLh0, p.salary-row_companyName__obLh0')
            anonymized_company = company_cell.select_one('span.salary-row_anonymizedCompany__DFcB6')

            if anonymized_company:
                company = 'Anonymous'
            elif company_name:
                company = company_name.text.strip()
            else:
                continue

            location_span = company_cell.select_one('span.MuiTypography-caption')
            location = location_span.text.split('|')[0].strip() if location_span else ''

            level_name = level_cell.text.strip() if level_cell else ''
            role = role_cell.text.strip() if role_cell else ''
            years_of_experience = yoe_cell.text.strip() if yoe_cell else ''
            years_at_company = yoe_company_cell.text.strip() if yoe_company_cell else ''
            total_comp = total_comp_cell.text.strip() if total_comp_cell else ''
            comp_breakdown = comp_breakdown_cell.text.strip() if comp_breakdown_cell else ''

            # Include entries with 'hidden' information, replacing 'hidden' with 'N/A'
            level_name = 'N/A' if level_name == 'hidden' else level_name
            role = 'N/A' if role == 'hidden' else role
            years_of_experience = 'N/A' if years_of_experience == 'hidden' else years_of_experience
            years_at_company = 'N/A' if years_at_company == 'hidden' else years_at_company

            if company and total_comp:
                data.append({
                    'Company': company,
                    'Location': location,
                    'Level Name': level_name,
                    'Role': role,
                    'Years of Experience': years_of_experience,
                    'Years at Company': years_at_company,
                    'Total Compensation': total_comp,
                    'Compensation Breakdown': comp_breakdown
                })

    logging.info(f"Successfully parsed {len(data)} salary entries")
    return data

def get_timestamped_filename(base_name):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{base_name}_{timestamp}.csv"

def scrape_levels_fyi(base_url, csv_filename, limit=1000):
    logging.info(f"Starting scraping with limit: {limit}")
    all_data = []
    offset = 0
    driver = setup_driver()
    consecutive_empty_pages = 0
    max_empty_pages = 3  # Stop after 3 consecutive empty pages

    try:
        while len(all_data) < limit and consecutive_empty_pages < max_empty_pages:
            url = f"{base_url}&offset={offset}" if offset > 0 else base_url
            html = fetch_page(driver, url, is_first_page=(offset == 0))
            data = parse_salary_data(html)

            if not data:
                consecutive_empty_pages += 1
                logging.info(f"No data found at offset {offset}. Empty pages: {consecutive_empty_pages}")
            else:
                consecutive_empty_pages = 0  # Reset the counter if we find data
                new_data = [item for item in data if item not in all_data]
                all_data.extend(new_data)
                logging.info(f"Scraped offset {offset}, new entries: {len(new_data)}, total entries: {len(all_data)}")

                # Save the new data to CSV
                df = pd.DataFrame(new_data)
                df.to_csv(csv_filename, mode='a', header=not pd.io.common.file_exists(csv_filename), index=False)
                logging.info(f"Appended {len(new_data)} entries to {csv_filename}")

            offset += 50  # Increment by 50 for each new page
            time.sleep(random.uniform(1, 3))  # Be nice to the server

        if consecutive_empty_pages == max_empty_pages:
            logging.info(f"Stopped after {max_empty_pages} consecutive empty pages")
        elif len(all_data) >= limit:
            logging.info(f"Reached the data limit of {limit} entries")

    finally:
        driver.quit()

    return all_data[:limit]

if __name__ == "__main__":
    base_url = "https://www.levels.fyi/t/software-engineer/locations/brazil?limit=50"
    base_filename = 'brazil_software_engineer_salaries'
    csv_filename = get_timestamped_filename(base_filename)
    logging.info(f"Starting scraper. Data will be saved to: {csv_filename}")
    data = scrape_levels_fyi(base_url, csv_filename)
    if data:
        logging.info(f"Scraping completed. Total entries saved to {csv_filename}: {len(data)}")
    else:
        logging.error("No data was scraped")
