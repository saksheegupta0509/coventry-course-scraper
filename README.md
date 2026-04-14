# Coventry University Course Scraper

## 📌 Project Overview

This project is a Python-based web scraper developed to extract course information from the official Coventry University website.

The scraper collects structured data for **exactly 5 undergraduate courses** and outputs the results in JSON format. The implementation strictly follows the assignment requirement of using only official university webpages and avoids over-engineering the parsing logic.

---

## 🚀 Features

* Scrapes data only from the official Coventry University website
* Automatically discovers course URLs
* Extracts data for **5 unique courses**
* Avoids duplicate entries
* Handles missing values using "NA"
* Outputs structured JSON data
* Simple and readable code structure

---

## 🛠️ Tech Stack

* Python
* Requests
* BeautifulSoup
* Regular Expressions (re)
* JSON

---

## ⚙️ Installation & Setup

### 1. Install Dependencies

```bash
pip install requests beautifulsoup4
```

---

## ▶️ How to Run

```bash
python coventry_scraper.py
```

After running the script, the output file will be generated:

```
output.json
```

---

## 📄 Output Format

The scraper generates a JSON file containing 5 course records.

Each record follows this structure:

```json
{
  "program_course_name": "",
  "university_name": "",
  "course_website_url": "",
  "campus": "",
  "country": "",
  "address": "",
  "study_level": "",
  "course_duration": "",
  "all_intakes_available": "",
  "mandatory_documents_required": "",
  "yearly_tuition_fee": "",
  "scholarship_availability": "",
  "gre_gmat_mandatory_min_score": "",
  "indian_regional_institution_restrictions": "",
  "class_12_boards_accepted": "",
  "gap_year_max_accepted": "",
  "min_duolingo": "",
  "english_waiver_class12": "",
  "english_waiver_moi": "",
  "min_ielts": "",
  "kaplan_test_of_english": "",
  "min_pte": "",
  "min_toefl": "",
  "ug_academic_min_gpa": "",
  "twelfth_pass_min_cgpa": "",
  "mandatory_work_exp": "",
  "max_backlogs": ""
}
```

---

## ⚠️ Assumptions & Notes

* Data is scraped only from official Coventry University webpages.

* Some fields may contain "NA" where data is not available on the webpage.

* Raw text extraction is used wherever applicable.

* Parsing logic is intentionally kept simple as per instruction:

  **"Do NOT over-engineer parsing/cleaning logic"**

* The focus is on correctness and reliability rather than full data coverage.

---

## 📁 Project Structure

```
coventry_scraper_project/

├── coventry_scraper_.py
├── output_.json
└── README.md
```

---

## ✅ Conclusion

This project demonstrates the ability to:

* Build a reliable web scraper using Python
* Work with real-world website data
* Handle missing values effectively
* Produce structured output in JSON format
* Follow assignment constraints and guidelines

---





