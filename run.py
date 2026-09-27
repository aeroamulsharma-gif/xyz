"""
Google Form Auto-Filler - TERMUX MOBILE VERSION
Runs directly on Android phone via Termux.
Supports: Email, Name, Radio, Checkboxes, Dropdowns, Short answers, Paragraphs, Grids, Likert.
Includes: Random interval mode (e.g. 10, 6, 4, 30 min random picks)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementNotInteractableException,
    ElementClickInterceptedException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import random
import time
import csv
import os
import shutil
from datetime import datetime


# ============================================================
#  ASCII LOGO / BANNER
# ============================================================
BANNER = r"""
 __   _  _  _  _  __     ____  _  _   __   ____  _  _   __
/ _\ ( \/ )/ )( \(  )   / ___)/ )( \ / _\ (  _ \( \/ ) / _\
\__ \/ \/ \) \/ (/ (_/\ \___ \) __ (/    \ )   // \/ \/    \
(___/\_)(_/\____/\____/ (____/\_)(_/\_/\_/(__\_)\_)(_/\_/\_/
"""

SUBTITLE = "     Google Form Auto-Filler  •  Termux Mobile Edition\n"


def print_banner():
    """Print the ASCII logo + subtitle"""
    print(BANNER)
    print(SUBTITLE)
    print("=" * 62)


# ============================================================
#  TERMUX CHROMIUM/CHROMEDRIVER PATH DETECTION
# ============================================================
def find_chromium_binary():
    paths = [
        shutil.which("chromium-browser"),
        shutil.which("chromium"),
        "/data/data/com.termux/files/usr/bin/chromium-browser",
        "/data/data/com.termux/files/usr/bin/chromium",
    ]
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def find_chromedriver_binary():
    paths = [
        shutil.which("chromedriver"),
        "/data/data/com.termux/files/usr/bin/chromedriver",
    ]
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


# ============================================================
#  (GoogleFormFiller class — unchanged from previous version)
# ============================================================
class GoogleFormFiller:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)
        self.short_wait = WebDriverWait(self.driver, 5)
        self._init_name_data()

    def _init_name_data(self):
        self.male_names = [
            "Aarav", "Abhishek", "Aditya", "Aman", "Amit", "Anil", "Arjun", "Ashish",
            "Bibek", "Bikash", "Bimal", "Binod", "Biraj", "Bishal",
            "Deepak", "Dinesh", "Dipesh", "Diwas",
            "Ganesh", "Gaurav", "Gopal",
            "Hari", "Hemant", "Himal",
            "Kiran", "Kishor", "Krishna", "Kumar",
            "Mahesh", "Manoj", "Milan", "Mohan",
            "Nabin", "Naresh", "Niraj", "Nirmal",
            "Pankaj", "Prabin", "Prakash", "Pramod", "Pratik", "Prem",
            "Rabin", "Rahul", "Raj", "Rajan", "Rajesh", "Rakesh", "Ram",
            "Ravi", "Rijan", "Ritesh", "Rohan", "Rohit", "Roshan",
            "Sachin", "Sagar", "Samir", "Sandeep", "Sanjay", "Santosh",
            "Shankar", "Shiva", "Shyam", "Subash", "Sudip", "Suman",
            "Sunil", "Suraj", "Sushil",
            "Ujjwal", "Umesh", "Uttam",
            "Yogesh", "Yubraj"
        ]
        self.female_names = [
            "Aarati", "Alisha", "Anita", "Anjali", "Anju", "Anusha",
            "Archana", "Asha", "Ashmita",
            "Babita", "Bandana", "Barsha", "Bhawana", "Bimala", "Bina",
            "Binita", "Bipana",
            "Deepa", "Deepika", "Durga",
            "Ganga", "Garima", "Gita",
            "Indira", "Ishwari",
            "Jamuna", "Janaki", "Jasmine", "Jenisha", "Jyoti",
            "Kabita", "Kalpana", "Kamala", "Kanchan", "Karuna", "Kavita",
            "Kriti", "Kumari", "Kusum",
            "Laxmi", "Lila", "Luna",
            "Mamata", "Manisha", "Maya", "Mina", "Mira",
            "Namrata", "Nisha", "Nirmala", "Nitu",
            "Pabitra", "Parvati", "Pooja", "Prabha", "Pratima", "Preeti",
            "Radha", "Rashmi", "Reena", "Renu", "Rita", "Roshani", "Rupa",
            "Sabina", "Sabita", "Sadhana", "Samjhana", "Sangita", "Saraswati",
            "Sarita", "Sarmila", "Shanti", "Sharmila", "Sita", "Smriti",
            "Srijana", "Sujata", "Sunita", "Sushma", "Swastika",
            "Tara", "Tulsi",
            "Uma", "Usha",
            "Yamuna", "Yogita"
        ]
        self.surnames = [
            "Adhikari", "Acharya", "Basnet", "Bhandari", "Bhatta",
            "Bhattarai", "Bista", "Budhathoki", "Chand", "Chaudhary", "Dahal",
            "Devkota", "Dhungana", "Ghimire", "Giri", "Gurung", "Gyawali",
            "Karki", "KC", "Khadka", "Khanal", "Khatiwada", "Khatri", "Koirala",
            "Kunwar", "Lama", "Lamichhane", "Magar", "Maharjan",
            "Mainali", "Malla", "Neupane", "Oli", "Pandey", "Pant", "Pathak",
            "Paudel", "Pokharel", "Poudel", "Rai", "Regmi", "Rijal",
            "Rimal", "Rokaya", "Sapkota", "Shah", "Shahi", "Shakya",
            "Sharma", "Sherpa", "Shrestha", "Sigdel", "Silwal", "Subedi",
            "Tamang", "Thapa", "Thapaliya", "Timalsina", "Tiwari", "Upreti",
            "Wagle", "Yadav"
        ]

    def generate_random_name(self, gender=None):
        if gender is None:
            gender = random.choice(["Male", "Female"])
        first_name = random.choice(self.male_names if gender == "Male" else self.female_names)
        surname = random.choice(self.surnames)
        return f"{first_name} {surname}"

    def generate_random_email(self, name=None):
        if name is None:
            name = self.generate_random_name()
        parts = name.lower().split()
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        formats = [f"{first}.{last}", f"{first}{last}", f"{first}_{last}"]
        username = random.choice(formats)
        if random.random() < 0.3:
            username += str(random.randint(1, 99))
        return f"{username}@gmail.com"

    def setup_driver(self, headless):
        #
        chrome_options = Options()
    
        # --- CHANGE 1: Explicit Chromium path ---
        chrome_options.binary_location = "/usr/bin/chromium"
    
        # --- CHANGE 3: Recommended argument list ---
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--remote-debugging-port=9222")

        mobile_agents = [
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 11; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Infinix X6819) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(mobile_agents)}")
        chrome_options.add_argument("--window-size=412,915")

        if headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        chromium_path = find_chromium_binary()
        chromedriver_path = find_chromedriver_binary()

        if chromium_path:
            chrome_options.binary_location = chromium_path
            print(f"  [INFO] Chromium: {chromium_path}")
        else:
            print("  [WARN] Chromium binary not found in PATH")

        if chromedriver_path:
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"  [INFO] ChromeDriver: {chromedriver_path}")
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def realistic_demographics(self):
        gender = random.choices(["Male", "Female"], weights=[50, 50])[0]
        age = random.choices(
            ["18–22", "23–26", "27–30", "31–34", "Above 34"],
            weights=[55, 35, 7, 2, 1])[0]
        province = random.choices(
            ["Koshi Province", "Madhesh Province", "Bagmati Province",
             "Gandaki Province", "Lumbini Province", "Karnali Province",
             "Sudurpaschim Province"],
            weights=[15, 12, 30, 20, 15, 4, 4])[0]
        education = random.choices(
            ["Secondary School (SEE)", "Higher Secondary School (+2/Diploma)",
             "Bachelor's Degree", "Master's Degree", "Doctorate Degree (PhD)"],
            weights=[2, 15, 65, 17, 1])[0]
        occupation = random.choices(
            ["Student", "Private Sector Employee", "Government Sector Employee",
             "Self-Employed", "Unemployed"],
            weights=[75, 15, 3, 4, 3])[0]
        income = random.choices(
            ["NPR 18,000 – 28,000", "NPR 28,001 – 38,000", "NPR 38,001 – 48,000",
             "NPR 48,001 – 58,000", "Above NPR 58,000"],
            weights=[40, 30, 15, 10, 5])[0]
        internet = random.choices(
            ["Less than 1 hour", "1–3 hours", "4–6 hours", "7–9 hours", "More than 9 hours"],
            weights=[2, 15, 35, 30, 18])[0]
        academic = random.choices(
            ["Daily", "Frequently", "Sometimes", "Rarely"],
            weights=[45, 35, 15, 5])[0]
        device = random.choices(
            ["Smartphone", "Laptop", "Desktop Computer", "Tablet", "Multiple Devices"],
            weights=[35, 40, 5, 2, 18])[0]
        training = random.choices(["Yes", "No"], weights=[35, 65])[0]

        full_name = self.generate_random_name(gender)
        email = self.generate_random_email(full_name)

        return {
            "gender": gender, "age": age, "province": province,
            "education": education, "occupation": occupation, "income": income,
            "internet": internet, "academic": academic, "device": device,
            "training": training, "name": full_name, "email": email,
        }

    def get_random_rating(self):
        return str(random.choices(["1", "2", "3", "4", "5"],
                                   weights=[10, 20, 30, 25, 15])[0])

    def get_random_checkbox_count(self, total):
        return random.randint(1, min(3, total))

    def get_short_answer(self):
        answers = [
            "I think this is very important.",
            "It depends on the situation.",
            "I have mixed feelings about this.",
            "This is something I've been thinking about.",
            "I believe more awareness is needed.",
            "Based on my experience, it matters a lot.",
            "I am not entirely sure.",
            "This affects me personally.",
            "I've noticed this becoming more relevant.",
            "It's an interesting topic."
        ]
        return random.choice(answers)

    def wait_for_page_load(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
            time.sleep(2)
        except TimeoutException:
            pass

    def get_all_questions(self):
        try:
            questions = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            return [q for q in questions if q.is_displayed()]
        except:
            return []

    def is_question_required(self, q):
        try:
            return "*" in q.text
        except:
            return False

    def get_question_text(self, q):
        try:
            titles = q.find_elements(By.CSS_SELECTOR, "div[role='heading']")
            if titles:
                return titles[0].text.strip()
            return q.text.split("\n")[0].strip() if q.text else ""
        except:
            return ""

    def get_question_type(self, q):
        try:
            if q.find_elements(By.CSS_SELECTOR, "input[type='email']"):
                if q.find_element(By.CSS_SELECTOR, "input[type='email']").is_displayed():
                    return "email"
            radios = [r for r in q.find_elements(By.CSS_SELECTOR, "div[role='radio']") if r.is_displayed()]
            if radios:
                groups = q.find_elements(By.CSS_SELECTOR, "div[role='radiogroup']")
                if len(groups) > 1:
                    return "grid"
                if len(radios) <= 7:
                    return "likert"
                return "radio"
            if [c for c in q.find_elements(By.CSS_SELECTOR, "div[role='checkbox']") if c.is_displayed()]:
                return "checkbox"
            if [d for d in q.find_elements(By.CSS_SELECTOR, "div[role='listbox']") if d.is_displayed()]:
                return "dropdown"
            if [i for i in q.find_elements(By.CSS_SELECTOR, "input[type='text']") if i.is_displayed()]:
                return "short_answer"
            if [t for t in q.find_elements(By.CSS_SELECTOR, "textarea") if t.is_displayed()]:
                return "paragraph"
            return "unknown"
        except:
            return "unknown"

    def scroll_to_element(self, element):
        for _ in range(3):
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", element)
                time.sleep(0.3)
                return True
            except:
                time.sleep(0.2)
        return False

    def safe_click(self, element):
        attempts = [
            lambda: element.click(),
            lambda: self.driver.execute_script("arguments[0].click();", element),
            lambda: ActionChains(self.driver).move_to_element(element).click().perform(),
            lambda: self.driver.execute_script("""
                var el = arguments[0];
                ['mousedown','mouseup','click'].forEach(function(t){
                    el.dispatchEvent(new MouseEvent(t, {bubbles:true, cancelable:true, view:window}));
                });
            """, element),
        ]
        for fn in attempts:
            try:
                fn()
                time.sleep(0.25)
                return True
            except:
                continue
        return False

    def answer_radio_question(self, q, answer_text=None):
        try:
            radios = [r for r in q.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                      if r.is_displayed() and r.size.get("height", 0) > 0]
            if not radios:
                return False
            if answer_text:
                for r in radios:
                    try:
                        t = (r.text.strip() or r.get_attribute("aria-label") or "")
                        if answer_text.lower() in t.lower() or t.lower() in answer_text.lower():
                            self.scroll_to_element(r)
                            self.safe_click(r)
                            return True
                    except:
                        continue
            choice = random.choice(radios)
            self.scroll_to_element(choice)
            self.safe_click(choice)
            return True
        except:
            return False

    def answer_checkbox_question(self, q):
        try:
            boxes = [c for c in q.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
                     if c.is_displayed() and c.size.get("height", 0) > 0]
            if not boxes:
                return False
            count = self.get_random_checkbox_count(len(boxes))
            for box in random.sample(boxes, count):
                self.scroll_to_element(box)
                self.safe_click(box)
                time.sleep(0.2)
            return True
        except:
            return False

    def answer_dropdown_question(self, q, answer_text=None):
        try:
            dd = q.find_element(By.CSS_SELECTOR, "div[role='listbox']")
            self.scroll_to_element(dd)
            self.safe_click(dd)
            time.sleep(0.8)
            options = [o for o in self.driver.find_elements(By.CSS_SELECTOR, "div[role='option']")
                       if o.is_displayed()]
            if not options:
                try:
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                except:
                    pass
                return False
            if answer_text:
                for o in options:
                    if answer_text.lower() in o.text.lower():
                        self.safe_click(o)
                        time.sleep(0.4)
                        return True
            self.safe_click(random.choice(options[1:] if len(options) > 1 else options))
            time.sleep(0.4)
            return True
        except:
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            except:
                pass
            return False

    def _set_input_value(self, elem, value):
        try:
            elem.click()
            time.sleep(0.2)
            elem.clear()
            elem.send_keys(value)
            time.sleep(0.2)
            if elem.get_attribute("value") != value:
                raise Exception("send_keys failed")
        except:
            self.driver.execute_script("""
                var el = arguments[0], val = arguments[1];
                el.focus();
                el.value = val;
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
            """, elem, value)

    def answer_email_question(self, q, email=None):
        try:
            field = q.find_element(By.CSS_SELECTOR, "input[type='email']")
            self.scroll_to_element(field)
            self._set_input_value(field, email or self.generate_random_email())
            return True
        except:
            return False

    def answer_short_answer_question(self, q, answer_text=None):
        try:
            emails = q.find_elements(By.CSS_SELECTOR, "input[type='email']")
            if emails and emails[0].is_displayed():
                return self.answer_email_question(q, answer_text)
            field = q.find_element(By.CSS_SELECTOR, "input[type='text']")
            self.scroll_to_element(field)
            self._set_input_value(field, answer_text or self.get_short_answer())
            return True
        except:
            return False

    def answer_paragraph_question(self, q, answer_text=None):
        try:
            ta = q.find_element(By.CSS_SELECTOR, "textarea")
            self.scroll_to_element(ta)
            self._set_input_value(ta, answer_text or self.get_short_answer())
            return True
        except:
            return False

    def answer_grid_question(self, q):
        try:
            rows = q.find_elements(By.CSS_SELECTOR, "div[role='radiogroup']") or \
                   q.find_elements(By.CSS_SELECTOR, "div[role='group']")
            for row in rows:
                try:
                    radios = [r for r in row.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                              if r.is_displayed()]
                    if radios:
                        c = random.choice(radios)
                        self.scroll_to_element(c)
                        self.safe_click(c)
                        time.sleep(0.2)
                except:
                    pass
            return True
        except:
            return False

    def answer_likert_question(self, q):
        try:
            radios = [r for r in q.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                      if r.is_displayed()]
            if not radios:
                return False
            if len(radios) <= 7:
                r = int(self.get_random_rating())
                choice = radios[r - 1] if r <= len(radios) else random.choice(radios)
                self.scroll_to_element(choice)
                self.safe_click(choice)
                return True
            for i in range(0, len(radios), 5):
                grp = radios[i:i + 5]
                if grp:
                    r = int(self.get_random_rating())
                    c = grp[r - 1] if r <= len(grp) else random.choice(grp)
                    self.scroll_to_element(c)
                    self.safe_click(c)
                    time.sleep(0.2)
            return True
        except:
            return False

    def match_demographic(self, question_text, demo):
        t = question_text.lower().strip()
        for p in ["name", "full name", "your name", "नाम", "fullname"]:
            if p in t:
                return "NAME:" + demo.get("name", "")
        for p in ["email", "gmail", "e-mail", "e mail", "इमेल", "mail"]:
            if p in t:
                return "EMAIL:" + demo.get("email", "")
        mappings = {
            "gender": ["gender", "sex", "पुरुष", "महिला"],
            "age": ["age", "उमेर", "वर्ष"],
            "province": ["province", "प्रदेश"],
            "education": ["education", "qualification", "degree", "शिक्षा"],
            "occupation": ["occupation", "profession", "job", "पेशा"],
            "income": ["income", "salary", "monthly income", "आम्दानी"],
            "internet": ["internet", "online", "इन्टरनेट"],
            "academic": ["academic", "study", "पढाइ"],
            "device": ["device", "mobile", "computer", "laptop", "उपकरण"],
            "training": ["training", "course", "trained", "तालिम"],
        }
        for k, kws in mappings.items():
            if any(kw in t for kw in kws):
                return demo.get(k)
        return None

    def fill_question(self, q, demo=None):
        q_type = self.get_question_type(q)
        q_text = self.get_question_text(q)
        if demo:
            ans = self.match_demographic(q_text, demo)
            if ans:
                if isinstance(ans, str) and ans.startswith("NAME:"):
                    return self.answer_short_answer_question(q, ans.replace("NAME:", ""))
                if isinstance(ans, str) and ans.startswith("EMAIL:"):
                    return self.answer_short_answer_question(q, ans.replace("EMAIL:", ""))
                if q_type == "radio":
                    return self.answer_radio_question(q, ans)
                if q_type == "dropdown":
                    return self.answer_dropdown_question(q, ans)
        return {
            "radio": lambda: self.answer_radio_question(q),
            "checkbox": lambda: self.answer_checkbox_question(q),
            "dropdown": lambda: self.answer_dropdown_question(q),
            "short_answer": lambda: self.answer_short_answer_question(q),
            "email": lambda: self.answer_short_answer_question(q),
            "paragraph": lambda: self.answer_paragraph_question(q),
            "grid": lambda: self.answer_grid_question(q),
            "likert": lambda: self.answer_likert_question(q),
        }.get(q_type, lambda: False)()

    def verify_all_required_filled(self):
        try:
            for q in self.get_all_questions():
                if self.is_question_required(q):
                    checks = [
                        q.find_elements(By.CSS_SELECTOR, "div[role='radio'][aria-checked='true']"),
                        q.find_elements(By.CSS_SELECTOR, "div[role='checkbox'][aria-checked='true']"),
                    ]
                    if any(checks):
                        continue
                    has_val = False
                    for sel in ["input[type='text']", "input[type='email']", "textarea"]:
                        for el in q.find_elements(By.CSS_SELECTOR, sel):
                            if el.is_displayed() and el.get_attribute("value"):
                                has_val = True
                                break
                        if has_val:
                            break
                    if not has_val:
                        return False
            return True
        except:
            return False

    def click_submit(self):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            for btn in self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']"):
                try:
                    txt = (btn.text.strip() or btn.get_attribute("aria-label") or "").lower()
                    if any(w in txt for w in ["submit", "पेस", "बुझाउ", "send"]):
                        self.scroll_to_element(btn)
                        self.safe_click(btn)
                        time.sleep(3)
                        return True
                except:
                    continue
            try:
                b = self.driver.find_element(By.CSS_SELECTOR, "div[jsname='M2UYVd']")
                if b.is_displayed():
                    self.safe_click(b)
                    time.sleep(3)
                    return True
            except:
                pass
            vis = [b for b in self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                   if b.is_displayed()]
            if vis:
                self.safe_click(vis[-1])
                time.sleep(3)
                return True
            return False
        except:
            return False

    def click_submit_another(self):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            for link in self.driver.find_elements(By.TAG_NAME, "a"):
                try:
                    txt = link.text.strip().lower()
                    href = link.get_attribute("href") or ""
                    if any(w in txt for w in ["another", "फेरि"]):
                        self.scroll_to_element(link)
                        self.safe_click(link)
                        time.sleep(3)
                        return True
                    if "viewform" in href:
                        self.driver.get(href)
                        time.sleep(3)
                        return True
                except:
                    continue
            return False
        except:
            return False

    def is_submission_successful(self):
        try:
            time.sleep(2)
            txt = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            return any(i in txt for i in [
                "thank you", "धन्यवाद", "response has been recorded",
                "submitted", "confirmation", "success", "another response"])
        except:
            return False

    def fill_form(self, url, demo=None):
        if demo is None:
            demo = self.realistic_demographics()
        try:
            self.driver.get(url)
            self.wait_for_page_load()
            questions = self.get_all_questions()
            filled = 0
            for q in questions:
                try:
                    if self.fill_question(q, demo):
                        filled += 1
                except:
                    continue
            if not self.verify_all_required_filled():
                for q in self.get_all_questions():
                    if self.is_question_required(q):
                        self.fill_question(q, demo)
            return filled, len(questions)
        except Exception as e:
            print(f"  [ERROR] {e}")
            return 0, 0

    def submit_form(self):
        try:
            return self.click_submit() and self.is_submission_successful()
        except:
            return False

    def save_log(self, num, status, error=None):
        fn = "form_submission_log.csv"
        exists = os.path.isfile(fn)
        with open(fn, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(["Response #", "Timestamp", "Status", "Error"])
            w.writerow([num, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, error or ""])

    def close(self):
        try:
            self.driver.quit()
        except:
            pass


# ============================================================
#  RANDOM INTERVAL PARSER
# ============================================================
def parse_intervals(raw):
    raw = raw.strip().lower()
    if raw in ("", "random"):
        return None, 1, 30
    if "," in raw:
        try:
            vals = [int(x.strip()) for x in raw.split(",") if x.strip()]
            return vals, min(vals), max(vals)
        except:
            pass
    if "-" in raw:
        try:
            a, b = raw.split("-")
            return None, int(a.strip()), int(b.strip())
        except:
            pass
    try:
        v = int(raw)
        return None, v, v
    except:
        return None, 1, 30


def pick_next_interval(fixed_values, min_m, max_m):
    if fixed_values:
        return random.choice(fixed_values)
    return random.randint(min_m, max_m)


# ============================================================
#  MAIN BATCH RUNNER
# ============================================================
def run_batch(url, count, headless, use_random, fixed_values, min_m, max_m):
    print_banner()
    filler = GoogleFormFiller(headless=headless)
    ok = 0
    fail = 0

    print(f"  Responses  : {count}")
    print(f"  Headless   : {headless}")
    if use_random:
        if fixed_values:
            print(f"  Intervals  : RANDOM from {fixed_values} minutes")
        else:
            print(f"  Intervals  : RANDOM {min_m}-{max_m} minutes")
    else:
        print(f"  Delay      : {min_m}-{max_m} seconds")
    print("=" * 62 + "\n")

    for i in range(1, count + 1):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Response {i}/{count}")

        try:
            demo = filler.realistic_demographics()
            print(f"  Name : {demo['name']}")
            print(f"  Email: {demo['email']}")

            filled, total = filler.fill_form(url, demo)
            if filled > 0:
                if filler.submit_form():
                    ok += 1
                    print(f"  ✔ Submitted ({filled}/{total})")
                    filler.save_log(i, "SUCCESS")
                    if i < count:
                        time.sleep(2)
                        filler.click_submit_another()
                else:
                    fail += 1
                    print("  ✘ Submit failed")
                    filler.save_log(i, "FAILED", "No confirmation")
            else:
                fail += 1
                print("  ✘ Nothing filled")
                filler.save_log(i, "FAILED", "No questions filled")
        except Exception as e:
            fail += 1
            print(f"  ✘ Error: {e}")
            filler.save_log(i, "ERROR", str(e))

        if i < count:
            if use_random:
                mins = pick_next_interval(fixed_values, min_m, max_m)
                secs = mins * 60
                print(f"  ⏳ Waiting {mins} min before next response...")
                elapsed = 0
                while elapsed < secs:
                    chunk = min(30, secs - elapsed)
                    time.sleep(chunk)
                    elapsed += chunk
                    rem = secs - elapsed
                    if rem > 0:
                        print(f"     {rem // 60}m {rem % 60}s remaining...")
            else:
                w = random.uniform(min_m, max_m)
                print(f"  ⏳ Waiting {w:.1f}s...")
                time.sleep(w)
            print()

    filler.close()

    print("\n" + "=" * 62)
    print(f"  DONE — {ok} success / {fail} failed")
    print("  Log: form_submission_log.csv")
    print("=" * 62 + "\n")
    return ok, fail


# ============================================================
#  ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print_banner()
    print("  Google Form Auto-Filler — Termux Edition")
    print("=" * 62)

    url = input("Form URL: ").strip()

    try:
        count = int(input("How many responses? (1-500): "))
        count = max(1, min(500, count))
    except ValueError:
        count = 1

    use_random = input("Use RANDOM INTERVAL mode? (y/n): ").strip().lower().startswith("y")

    fixed_values = None
    min_m, max_m = 1, 30

    if use_random:
        print("\nInterval options:")
        print("  'random'        -> random 1-30 min")
        print("  '5-30'          -> random 5-30 min")
        print("  '10, 6, 4, 30'  -> picks one randomly each time")
        print("  '15'            -> fixed 15 min")
        raw = input("Enter interval config: ").strip()
        fixed_values, min_m, max_m = parse_intervals(raw)
        if fixed_values:
            print(f"\n  → Will randomly pick from: {fixed_values} minutes")
        else:
            print(f"\n  → Random between {min_m} and {max_m} minutes")
    else:
        try:
            min_m = float(input("Min delay (seconds): "))
            max_m = float(input("Max delay (seconds): "))
        except ValueError:
            min_m, max_m = 30, 60

    headless = input("Headless mode? (y/n): ").strip().lower().startswith("y")

    input("\nPress ENTER to start...")

    run_batch(url, count, headless, use_random, fixed_values,
              int(min_m) if use_random else min_m,
              int(max_m) if use_random else max_m)
