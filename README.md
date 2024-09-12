# Comp-Scraping

[![tests](https://github.com/lucasheriques/comp-scraping/actions/workflows/tests.yml/badge.svg)](https://github.com/lucasheriques/comp-scraping/actions/workflows/tests.yml)

Comp-Scraping is a web scraper designed to collect salary data for software engineers in Brazil from levels.fyi. This project uses Python and Selenium to automate data collection and analysis.

Want to check out the last analysis? [Open the notebook here](https://github.com/lucasheriques/comp-scraping/blob/main/comp_scraping/data_analysis.ipynb).

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
   git clone https://github.com/lucasheriques/comp-scraping.git
   cd comp-scraping
   ```

4. Install dependencies using Poetry:

   ```
   poetry install
   ```

5. Activate the virtual environment:
   ```
   poetry shell
   ```

## Usage

### Scraper

To run the scraper:

```
poetry run scrape
```

This will start the scraping process and save the data to a CSV file in the `data` directory.

### Data Analysis

To analyze the scraped data using a Jupyter notebook:

1. Ensure you're in the project's virtual environment:

   ```
   poetry shell
   ```

2. Run the following command to launch the Jupyter notebook:

   ```
   poetry run analyze
   ```

   This will start the Jupyter notebook server and directly open the data analysis notebook in your default web browser.

3. [Open the notebook here](http://localhost:8888/doc/tree/comp_scraping/data_analysis.ipynb). You can run the cells to load the most recent data, perform analysis, and visualize the results.

4. To re-run the analysis with updated data, make sure to restart the kernel and run all cells again.

Note: The analysis notebook automatically uses the most recent CSV file in the `data` directory, so you don't need to update the file path manually.
