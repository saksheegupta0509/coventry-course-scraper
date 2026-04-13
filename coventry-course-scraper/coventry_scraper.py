import requests
from bs4 import BeautifulSoup
import re

import json

required_fields = ["program_course_name",
"university_name",
"course_website_url",
"campus",
"country",
"address",
"study_level",
"course_duration",
"all_intakes_available",
"mandatory_documents_required",
"yearly_tuition_fee",
"scholarship_availability",
"gre_gmat_mandatory_min_score",
"indian_regional_institution_restrictions",
"class_12_boards_accepted",
"gap_year_max_accepted",
"min_duolingo",
"english_waiver_class12",
"english_waiver_moi",
"min_ielts",
"kaplan_test_of_english",
"min_pte",
"min_toefl" ,
"ug_academic_min_gpa",
"twelfth_pass_min_cgpa",
"mandatory_work_exp",
"max_backlogs"
]

def create_empty_data():
    return {key: "NA" for key in required_fields}

def get_course_links():
    url = "https://www.coventry.ac.uk/search/?search=&contentType=newcoursepage&sl=140_"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Filter only course links
        if "/course-structure/ug/" in href:
            if href.startswith("/"):
                href = "https://www.coventry.ac.uk" + href

            links.add(href)

    return list(links)[:10]

def scrape_course(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    data = create_empty_data()
    data["course_website_url"] = url
    data["university_name"] = "Coventry University"
    data["country"] = "UK"
    data["study_level"] = "Undergraduate"

    # Course name
    title = soup.find("h1")
    if title:
        data["program_course_name"] = title.get_text(strip=True)

    # Get full page text
    page_text = soup.get_text(separator=" ").lower()

    # Extract basic fields (simple approach)
    duration_matches = re.findall(r"\b\d+\s+year[s]?\b", page_text)
    if duration_matches:
        data["course_duration"] = duration_matches[0]

    # Intakes
    intakes_match = re.search(r"(?:intake[s]?|start date[s]?|commencement)(?:\s*of)?\s*(january|february|march|april|may|june|july|august|september|october|november|december)(?:\s*(?:and|,|\s*or\s*)?(january|february|march|april|may|june|july|august|september|october|november|december))*", page_text)
    if intakes_match:
        # Join all captured month groups, filtering out None values
        intakes = [group.capitalize() for group in intakes_match.groups() if group]
        data["all_intakes_available"] = ", ".join(intakes)
    elif "september" in page_text:
        data["all_intakes_available"] = "September" # Fallback if specific regex fails but 'september' is present

    ielts_match = re.search(r"ielts(?:\D*?)?(\d\.\d)", page_text)
    if ielts_match:
        data["min_ielts"] = ielts_match.group(1)

    toefl_match = re.search(r"toefl(?:\D*?)?(\d{2,3})", page_text)
    if toefl_match:
        data["min_toefl"] = toefl_match.group(1)

    pte_match = re.search(r"pte(?:\D*?)?(\d{2})", page_text)
    if pte_match:
        data["min_pte"] = pte_match.group(1)

    # Refined Duolingo extraction
    duolingo_match = re.search(r"(?:duolingo|det)(?:\D*?)?(\d{2,3})", page_text, re.IGNORECASE)
    if duolingo_match:
        data["min_duolingo"] = duolingo_match.group(1)

    # Refined GRE/GMAT extraction to capture score and use correct group
    gre_gmat_match = re.search(r"(?:gre|gmat)(?:\s+score)?(?:\D*?)?(\d{2,4})", page_text, re.IGNORECASE)
    if gre_gmat_match:
        data["gre_gmat_mandatory_min_score"] = gre_gmat_match.group(1)

    fee_match = re.search(r"£\d{1,3}(?:,\d{3})*", page_text)
    if fee_match:
        data["yearly_tuition_fee"] = fee_match.group(0)

    if "scholarship" in page_text or "funding" in page_text:
        data["scholarship_availability"] = "Yes"

    # Campus - Check for other campuses besides 'Coventry' if present
    # For simplicity, if 'coventry' is in text, assume Coventry campus
    if "coventry" in page_text:
        data["campus"] = "Coventry"

    # New fields to extract based on assignment requirements (raw text acceptable)

    # Address: Often in footer or contact page. Will try to find a generic address pattern or block
    address_match = re.search(r"coventry university\s*,\s*[\w\s,]+\s*united kingdom", page_text, re.IGNORECASE)
    if address_match:
        data["address"] = address_match.group(0).replace('\n', ' ').strip()
    else:
        # Fallback to look for a post code
        postcode_match = re.search(r"[a-z]{1,2}\d[a-z\d]?\s*\d[a-z]{2}", page_text)
        if postcode_match:
            # Try to get a surrounding paragraph if a postcode is found
            # This is a very rough approach, might need refinement if not catching well
            try:
                address_start = page_text.rfind('.', 0, postcode_match.start()) + 1
                address_end = page_text.find('.', postcode_match.end())
                if address_start != -1 and address_end != -1:
                    data["address"] = page_text[address_start:address_end+1].strip().replace('\n', ' ')
            except:
                pass

    # Mandatory Documents Required
    docs_match = re.search(r"(?:mandatory documents required|documents you need|application checklist)(?:\s*[:\-]?\s*)([\w\s,;\(\)&\./-]{20,200})", page_text, re.IGNORECASE)
    if docs_match:
        data["mandatory_documents_required"] = docs_match.group(1).strip()
    else:
        # Broader search for 'entry requirements' section
        entry_requirements_section = re.search(r"entry requirements(.*?)(?:how to apply|apply now|fees and funding|course structure)", page_text, re.DOTALL | re.IGNORECASE)
        if entry_requirements_section:
            docs_keywords = re.search(r"(?:documents|transcripts|certificates|personal statement|visa requirements)(.*?)(?:\n\n|\.|upload)", entry_requirements_section.group(1), re.DOTALL | re.IGNORECASE)
            if docs_keywords:
                data["mandatory_documents_required"] = docs_keywords.group(0).strip().replace('\n', ' ')

    # Indian Regional Institution Restrictions (broad search)
    india_restriction_match = re.search(r"(?:indian(?:\s+regional)?\s+institution restrictions|india admissions|requirements for indian students)(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if india_restriction_match:
        data["indian_regional_institution_restrictions"] = india_restriction_match.group(1).strip().replace('\n', ' ')

    # Class 12 Boards Accepted
    class12_match = re.search(r"(?:class 12 boards accepted|12th grade qualifications|indian school certificates)(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if class12_match:
        data["class_12_boards_accepted"] = class12_match.group(1).strip().replace('\n', ' ')

    # Gap Year Max Accepted
    gap_year_match = re.search(r"(?:gap year(?:\s+policy)?|maximum gap accepted)(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if gap_year_match:
        data["gap_year_max_accepted"] = gap_year_match.group(1).strip().replace('\n', ' ')

    # English Waiver Class 12
    english_waiver_class12_match = re.search(r"english waiver class 12(?:\s*standards)?(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if english_waiver_class12_match:
        data["english_waiver_class12"] = english_waiver_class12_match.group(1).strip().replace('\n', ' ')

    # English Waiver MOI
    english_waiver_moi_match = re.search(r"english waiver(?:\s+for)? medium of instruction(?:\s*\(moi\))?(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if english_waiver_moi_match:
        data["english_waiver_moi"] = english_waiver_moi_match.group(1).strip().replace('\n', ' ')

    # Kaplan Test of English
    kaplan_match = re.search(r"kaplan test of english(?:\D*?)?(\d{2,3})?", page_text, re.IGNORECASE)
    if kaplan_match and kaplan_match.group(1):
        data["kaplan_test_of_english"] = kaplan_match.group(1)
    elif kaplan_match:
        data["kaplan_test_of_english"] = "Mentioned on page"

    # UG Academic Min GPA / Twelfth Pass Min CGPA
    gpa_match = re.search(r"(?:gpa|cgpa|grade point average)(?:\D*?)?(\d\.\d)", page_text, re.IGNORECASE)
    if gpa_match:
        data["ug_academic_min_gpa"] = gpa_match.group(1)
        data["twelfth_pass_min_cgpa"] = gpa_match.group(1) # Using same for both, as assignment allows raw text

    # Mandatory Work Experience
    work_exp_match = re.search(r"(?:mandatory work experience|minimum work experience)(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if work_exp_match:
        data["mandatory_work_exp"] = work_exp_match.group(1).strip().replace('\n', ' ')

    # Max Backlogs
    backlogs_match = re.search(r"(?:maximum backlogs accepted|backlog policy)(.*?)(?:\n\n|\.)", page_text, re.DOTALL | re.IGNORECASE)
    if backlogs_match:
        data["max_backlogs"] = backlogs_match.group(1).strip().replace('\n', ' ')

    return data

def main():
    print("Fetching course links...")
    # Get all potential course links
    course_links = get_course_links()

    results = []
    scraped_course_names = set()
    target_unique_courses = 5

    for link in course_links:
        if len(results) >= target_unique_courses:
            break # Stop once 5 unique courses are found

        print(f"Scraping: {link}")
        try:
            course_data = scrape_course(link)
            course_name = course_data.get("program_course_name")

            if course_name and course_name not in scraped_course_names:
                results.append(course_data)
                scraped_course_names.add(course_name)
                print(f"Added unique course: {course_name}")
            else:
                print(f"Skipping duplicate or unnamed course: {course_name if course_name else 'Unnamed'}")

        except Exception as e:
            print(f"Error scraping {link}: {e}")

    # Ensure we only save exactly 5 courses if possible
    final_results = results[:target_unique_courses]

    print(f"\nScraped {len(final_results)} unique courses.")

    # Save output
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

    print("\n✅ Done! Data saved in output.json")


# RUN PROGRAM

if __name__ == "__main__":
    main()
