# Comp-Scraping

Comp-Scraping is a web scraper designed to collect salary data for software engineers in Brazil from levels.fyi. This project uses Python and Selenium to automate data collection and analysis.

## Tools and Technologies

- Python 3.12+
- Poetry (for dependency management)
- Selenium (for web scraping)
- BeautifulSoup4 (for HTML parsing)
- Pandas (for data manipulation)
- Pytest (for testing)

## Setup

1. Ensure you have Python 3.12 or higher installed on your system.

2. Install Poetry if you haven't already:

   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Clone the repository:

   ```
   git clone https://github.com/your-username/comp-scraping.git
   cd comp-scraping
   ```

4. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Usage

To run the scraper:

```
poetry run scrape
```

This will start the scraping process and save the data to a CSV file in the `data` directory.
