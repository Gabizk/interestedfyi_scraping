# Interested.fyi Job Scraper

This Python script automatically scrapes job offers from interested.fyi and saves them in dated JSON files.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. You must have Google Chrome or Chromium installed for Selenium to work (the script uses headless Chrome by default).

3. Create a `.env` file with the following content:
```
BASE_URL=https://www.interested.fyi
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will create a JSON file named `jobs_YYYY-MM-DD.json` containing all scraped job offers.
