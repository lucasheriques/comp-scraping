import os
import time
import random
import logging
import pandas as pd
from datetime import datetime  # Add this import
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        logging.info(f"Table element found on the page")

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        logging.info(f"Table rows found on the page")

        if is_first_page:
            input("Press Enter after manually inspecting and scrolling the page...")

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

    for row in rows:
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

            company = parse_company_name(company_cell)
            if not company:
                continue

            data.append({
                'Company': company,
                'Location': parse_location(company_cell),
                'Level Name': handle_hidden_value(parse_cell_text(level_cell)),
                'Role': handle_hidden_value(parse_cell_text(role_cell)),
                'Years of Experience': handle_hidden_value(parse_cell_text(yoe_cell)),
                'Years at Company': handle_hidden_value(parse_cell_text(yoe_company_cell)),
                'Total Compensation': parse_cell_text(total_comp_cell),
                'Compensation Breakdown': parse_cell_text(comp_breakdown_cell)
            })

    logging.info(f"Successfully parsed {len(data)} salary entries")
    return data

def parse_company_name(company_cell):
    company_name = company_cell.select_one('a.salary-row_companyName__obLh0, p.salary-row_companyName__obLh0')
    anonymized_company = company_cell.select_one('span.salary-row_anonymizedCompany__DFcB6')
    return 'Anonymous' if anonymized_company else (company_name.text.strip() if company_name else None)

def parse_location(company_cell):
    location_span = company_cell.select_one('span.MuiTypography-caption')
    return location_span.text.split('|')[0].strip() if location_span else ''

def parse_cell_text(cell):
    return cell.text.strip() if cell else ''

def handle_hidden_value(value):
    return 'N/A' if value == 'hidden' else value

def get_timestamped_filename(base_name):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{base_name}_{timestamp}.csv"

def ensure_data_directory():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def scrape_levels_fyi(base_url, csv_filename, limit=1000):
    logging.info(f"Starting scraping with limit: {limit}")
    all_data = []
    offset = 0
    driver = setup_driver()
    consecutive_empty_pages = 0
    max_empty_pages = 3  # Stop after 3 consecutive empty pages

    data_dir = ensure_data_directory()
    csv_path = os.path.join(data_dir, csv_filename)

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
                df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
                logging.info(f"Appended {len(new_data)} entries to {csv_path}")

            offset += 50
            time.sleep(random.uniform(1, 3))

    finally:
        driver.quit()

    return all_data[:limit]

def main():
    base_url = "https://www.levels.fyi/t/software-engineer/locations/brazil?limit=50"
    base_filename = 'brazil_software_engineer_salaries'
    csv_filename = get_timestamped_filename(base_filename)
    logging.info(f"Starting scraper. Data will be saved to: data/{csv_filename}")
    data = scrape_levels_fyi(base_url, csv_filename)
    if data:
        logging.info(f"Scraping completed. Total entries saved to data/{csv_filename}: {len(data)}")
    else:
        logging.error("No data was scraped")

if __name__ == "__main__":
    main()
