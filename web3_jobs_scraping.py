# This script scrapes job offers from each of the pages
# of the companies listed on the website interested.fyi. You can find the list of URLs in the file company_urls.json
# The script uses Selenium to scrape the job offers from each page and saves them in a JSON file
# At the time of updating this script, the website interested.fyi lists around 230 companies
# Interested.fyi is a website that lists job offers from web3 companies
# Scraping the job offers may take around 15 minutes
# It returns around 2-3k job offers that I filter based on keywords to discard some locations and positions
# Then I use ChatGPT 4.1 mini for a final filter, it consumes approx 30k input and 0.5k output tokens
# I include my summary CV to filter the job offers based on my experience and skills




# === 1. scrape_250_companies.py ===

import json
import time
import logging
from dotenv import load_dotenv
import os
from selenium import webdriver

# Automatically load environment variables from .env
load_dotenv()
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)


def scrape_and_upload():
    logging.info("=== Starting scrape run for ALL companies ===")

    # 1) Load ALL URLs
    try:
        with open("company_urls.json", "r", encoding="utf-8") as f:
            company_urls = json.load(f)  # <--- NO slicing, procesa todas
    except Exception as e:
        logging.error(f"Failed to load company_urls.json: {e}")
        return

    all_jobs = []

    for url in company_urls:
        logging.info(f"→ Processing {url}")
        chrome_opts = Options()
        chrome_opts.add_argument('--headless')
        chrome_opts.add_argument('--no-sandbox')
        chrome_opts.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_opts)

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)

            # Company name
            try:
                elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "div.text-blue-700.text-5xl.font-bold.font-heading"
                    ))
                )
                company = elem.text.strip()
            except:
                company = "UNKNOWN"
                logging.warning(f"Company name missing at {url}")

            logging.info(f"[{company}] scraping job rows")
            tbody = driver.find_element(By.CSS_SELECTOR, "table tbody")
            for row in tbody.find_elements(By.TAG_NAME, "tr"):
                try:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if len(tds) < 2:
                        continue

                    link_cell, loc_cell = tds[0], tds[1]
                    a = link_cell.find_element(By.TAG_NAME, "a")
                    spans = a.find_elements(By.TAG_NAME, "span")

                    position = spans[0].text.strip() if spans else ""
                    department = ""
                    for s in spans:
                        txt = s.text.strip()
                        if txt != position and "Verified" not in txt:
                            department = txt
                            break
                    location = loc_cell.text.strip()
                    external_link = a.get_attribute("href")

                    all_jobs.append({
                        "company":       company,
                        "position":      position,
                        "location":      location,
                        "department":    department,
                        "external_link": external_link
                    })
                except Exception as row_err:
                    logging.warning(f"[{company}] row parse error: {row_err}")
        except Exception as page_err:
            logging.error(f"Failed scraping {url}: {page_err}")
        finally:
            driver.quit()

    # 3) Save JSON
    output_file = "jobs_companies_250.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved {len(all_jobs)} jobs to {output_file}")
    except Exception as e:
        logging.error(f"Could not write {output_file}: {e}")
        return

    logging.info("=== Scrape run complete ===")

# === 2. Filter_key_words.py ===

# Banned words (case-insensitive, can appear anywhere in the string)
BANNED_WORDS = [
    "VP", "CEO", "CTO", "Quantitiative", "legal"... #Include here your banned words 
]

INPUT_FILE = "jobs_companies_250.json"
OUTPUT_FILE = "jobs_250_filter_position.json"

def contiene_palabra_baneada(text):
    """Devuelve True si el texto contiene alguna palabra prohibida."""
    text_lower = text.lower()
    for word in BANNED_WORDS:
        if word.lower() in text_lower:
            return True
    return False

# Locations where I want the job offer to be
KEEP_DEPT_WORDS = [
    "Vienna", "Brussels", "Sofia"...
]

def contains_dept_word(text):
    """Returns True if the text contains any department keyword."""
    text_lower = text.lower()
    for word in KEEP_DEPT_WORDS:
        if word.lower() in text_lower:
            return True
    return False

def filter_key_words_main():
    # Read the original file
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total objects in the original file: {len(data)}")

    # Filter objects by position
    filtered = [obj for obj in data if not contains_banned_word(obj.get("position", ""))]
    print(f"Objects remaining after filtering by 'position': {len(filtered)}")

    # Filter by department (keep only those containing keywords and apply Remote+US logic)
    filtrados_dept = []
    for obj in filtrados:
        dept = obj.get("department", "")
        if contiene_palabra_dept(dept):
            filtrados_dept.append(obj)
    print(f"Objetos restantes tras filtrar por 'department': {len(filtrados_dept)}")

    # Remove the 'location' key from each object before saving
    for obj in filtrados_dept:
        obj.pop("location", None)

    # Save the new file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtrados_dept, f, indent=2, ensure_ascii=False)
    print(f"Archivo filtrado guardado como {OUTPUT_FILE}")

# === 3. jobs_250_GPT_filter2.py ===

import openai
import os

# OpenAI configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está definido en las variables de entorno")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

INPUT_FILE_GPT = "jobs_250_filter_position.json"
OUTPUT_FILE_GPT = "jobs_250_GPT_filter2.json"


# Include your CV here, this is an example of the prompt that I have used
SYSTEM_PROMPT = (
    "You are a Job-Offer Analyst. "
    "Return JSON: {\"match\": true/false} based on whether the job title fits the CV.\n"
    "CV SUMMARY:\n"
    "EXPERIENCE\n"
    "• Advisor –   "
    "• Co-Founder & Business Development Lead" 
    "EDUCATION\n"
    "• Executive MBA  "
    "• Postgraduate in Marketing & Management Development  "
    "SKILLS & TOOLS\n"
    "AI • Automation • Python • Blockchain • SaaS GTM • B2B Sales • Negotiation • CRM • Public Speaking • Team Building • Investor Relations • Google Workspace • MS Office • Notion • Figma • Slack  \n"
    "LANGUAGES\n"
    "Spanish (native), English C2\n"
)

def gpt_match_title(title: str) -> bool:
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"Job title: {title}"}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        functions=[{
            "name": "set_match",
            "parameters": {
                "type": "object",
                "properties": {"match": {"type": "boolean"}}
            }
        }],
        function_call={"name": "set_match"},
        temperature=0,
        max_tokens=4
    )
    arguments = response.choices[0].message.function_call.arguments
    try:
        match_obj = json.loads(arguments)
        return match_obj["match"]
    except Exception:
        if isinstance(arguments, str):
            if "true" in arguments.lower():
                return True
            if "false" in arguments.lower():
                return False
        return False

def gpt_filter_main():
    with open(INPUT_FILE_GPT, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    print(f"Total de ofertas a analizar: {len(jobs)}")
    jobs_with_gpt = []
    for idx, obj in enumerate(jobs, 1):
        title = obj.get("position", "")
        is_match = gpt_match_title(title)
        obj["GPT"] = is_match
        print(f"[{idx}/{len(jobs)}] {title} -> {is_match}")
        jobs_with_gpt.append(obj)
    filtered_jobs = [obj for obj in jobs_with_gpt if obj["GPT"]]
    print(f"Ofertas que cumplen los criterios GPT: {len(filtered_jobs)}")
    with open(OUTPUT_FILE_GPT, "w", encoding="utf-8") as f:
        json.dump(filtered_jobs, f, indent=2, ensure_ascii=False)
    print(f"Archivo generado: {OUTPUT_FILE_GPT}")

# === 4. airtable_append.py ===

import requests
from datetime import datetime
import os

# Airtable configuration
AIRTABLE_TOKEN = os.environ.get("AIRTABLE_TOKEN")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
TABLE_ID = os.environ.get("AIRTABLE_TABLE_ID")
if not AIRTABLE_TOKEN or not BASE_ID or not TABLE_ID:
    raise ValueError("Alguna variable de entorno de Airtable no está definida (AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)")
API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

INPUT_FILE_AT = "jobs_250_GPT_filter2.json"
BATCH_SIZE = 10  # Airtable permite hasta 10 registros por petición
RATE_LIMIT_SLEEP = 0.25  # 4 peticiones por segundo máx

# Table fields - must match Airtable exactly
FIELD_MAP = {
    "Position": "position",
    "Company": "company",
    "Location": "department",
    "URL": "external_link",
    "Status": "status",
    "Date": "date"
}

STATUS_VALUE = "New"

def get_existing_urls():
    """Obtiene todas las URLs ya presentes en el campo 'URL' de la tabla."""
    existing_urls = set()
    offset = None
    while True:
        params = {"fields[]": ["URL"]}
        if offset:
            params["offset"] = offset
        resp = requests.get(API_URL, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        for record in data.get("records", []):
            url = record["fields"].get("URL")
            if url:
                existing_urls.add(url)
        offset = data.get("offset")
        if not offset:
            break
        time.sleep(RATE_LIMIT_SLEEP)
    return existing_urls

def airtable_append_main():
    # 1. Leer ofertas nuevas
    with open(INPUT_FILE_AT, "r", encoding="utf-8") as f:
        offers = json.load(f)
    print(f"Total de ofertas a procesar: {len(offers)}")

    # 2. Leer URLs ya existentes
    print("Obteniendo URLs ya presentes en la tabla de Airtable...")
    existing_urls = get_existing_urls()
    print(f"URLs ya presentes: {len(existing_urls)}")

    # 3. Filtrar ofertas nuevas
    new_offers = [o for o in offers if o.get("external_link") not in existing_urls]
    print(f"Ofertas nuevas a insertar: {len(new_offers)}")

    # 4. Preparar e insertar en batches
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = []
    for obj in new_offers:
        record = {
            "fields": {
                "Position": obj.get("position", ""),
                "Company": obj.get("company", ""),
                "Location": obj.get("department", ""),
                "URL": obj.get("external_link", ""),
                "Status": STATUS_VALUE,
                "Date": now_str
            }
        }
        records.append(record)

    # Insert in batches of 10
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]
        payload = {"records": batch}
        resp = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
        if resp.status_code >= 400:
            print(f"[ERROR] Batch {i//BATCH_SIZE+1}: {resp.status_code} {resp.text}")
        else:
            print(f"Batch {i//BATCH_SIZE+1}: Insertados {len(batch)} registros.")
        time.sleep(RATE_LIMIT_SLEEP)

    print("Proceso completado.")

# === Combined Entry Point ===

def main():
    scrape_and_upload()
    filter_key_words_main()
    gpt_filter_main()
    airtable_append_main()

if __name__ == "__main__":
    main()
