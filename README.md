# Interested.fyi Web3 Job Scraper

This Python script (`web3_jobs_scraping.py`) scrapes job offers from all companies listed on [interested.fyi](https://www.interested.fyi), filters them with keywords and an AI model, and uploads the final results to Airtable.

---

## Features
- Scrapes all company job pages using Selenium.
- Filters jobs by banned words and preferred locations/departments.
- Uses OpenAI (GPT-4o mini) to further filter jobs based on your CV.
- Uploads the final list to Airtable, avoiding duplicates.
- Keeps your secrets safe using a `.env` file (which is gitignored).

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Google Chrome or Chromium** for Selenium (the script uses headless Chrome by default).

3. **Create a `.env` file** in this folder with the following variables:
   ```ini
   OPENAI_API_KEY=your_openai_api_key_here
   AIRTABLE_TOKEN=your_airtable_token_here
   AIRTABLE_BASE_ID=your_airtable_base_id_here
   AIRTABLE_TABLE_ID=your_airtable_table_id_here
   ```
   > **Note:** `.env` is gitignored for your security.

4. **Make sure you have `company_urls.json`** with the list of company URLs to scrape (one per line or as a JSON array).

---

## Usage

Run the full pipeline with:
```bash
python web3_jobs_scraping.py
```

The pipeline will:
1. Scrape job offers from all companies in `company_urls.json`.
2. Filter jobs by banned words and department/location keywords.
3. Use GPT to further filter jobs based on your CV.
4. Upload the results to Airtable, skipping duplicates.

Intermediate results are saved as JSON files for each step.

---

## Git tracking

This repo is configured to only track:
- `web3_jobs_scraping.py`
- `README.md`
- `company_urls.json`

All other files, including `.env` and outputs, are ignored by git.

---

## Customization
- Edit the `SYSTEM_PROMPT` in the script to match your CV for better filtering.
- Adjust banned words or department keywords directly in the script if needed.

---

For any questions or improvements, feel free to open an issue or PR!
