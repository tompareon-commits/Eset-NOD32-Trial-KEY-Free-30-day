
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random
import string
import os
import re

def dprint(msg):
    print(msg, flush=True)

class EsetRegister:
    def __init__(self):
        options = Options()
        # options.add_argument("--headless=new") 
        options.add_argument("--disable-search-engine-choice-screen")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.maximize_window()
        self.email = ""
        self.password = self.generate_password()
        self.first_name = random.choice(["Oleg", "Ivan", "Petro", "Dmytro", "Andriy", "Mykola", "Volodymyr", "Oleksandr", "Serhiy", "Maksym"])
        self.last_name = random.choice(["Kovalenko", "Bondarenko", "Tkachenko", "Shevchenko", "Melnyk", "Boyko", "Kravchenko", "Kozak", "Oliynyk", "Shevchuk"])
        self.full_name = f"{self.first_name} {self.last_name}"
        self.mohmal_handle = None
        self.eset_handle = None

    def generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(12))

    def get_temp_email(self):
        dprint("Navigating to Mohmal...")
        self.driver.get("https://www.mohmal.com/en")
        self.mohmal_handle = self.driver.current_window_handle
        time.sleep(2)
        
        try:
            consent_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".halal-btn-accept"))
            )
            consent_btn.click()
            dprint("Clicked Consent Overlay")
            time.sleep(1)
        except:
            pass

        try:
            random_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "rand"))
            )
            random_btn.click()
            dprint("Clicked 'Random Name'")
        except Exception as e:
            dprint(f"Could not find 'Random Name' button: {e}")
            return False

        time.sleep(2)
        try:
            email_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".email"))
            )
            self.email = email_element.text
            dprint(f"Got email: {self.email}")
            return True
        except Exception as e:
            dprint(f"Could not find email element: {e}")
            return False
            
    def register_eset_step1(self):
        dprint("Navigating to ESET Register...")
        self.driver.switch_to.new_window('tab')
        self.eset_handle = self.driver.current_window_handle
        self.driver.get("https://login.eset.com/register/index")
        
        try:
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.send_keys(self.email)
            dprint("Filled email")
        except Exception as e:
            dprint(f"Could not find email input: {e}")
            return False

        try:
            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='register-continue-button']"))
            )
            continue_btn.click()
            dprint("Clicked Continue")
        except Exception as e:
            dprint(f"Could not find 'Continue' button: {e}")
            return False
            
        return True

    def register_eset_step2(self):
        dprint("Waiting for Step 2...")
        time.sleep(2)
        
        try:
            pass_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            pass_input.send_keys(self.password)
            dprint("Filled password")
        except Exception as e:
            dprint(f"Could not find password input: {e}")
            return False

        try:
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-label='register-create-account-button']")
            submit_btn.click()
            dprint("Clicked Create Account")
        except Exception as e:
             dprint(f"Could not find Create Account button: {e}")

    def check_email_verification(self):
        dprint("Checking email verification on Mohmal...")
        self.driver.switch_to.window(self.mohmal_handle)
        
        for i in range(12): 
            try:
                dprint(f"Check attempt {i+1}...")
                refresh_btn = self.driver.find_element(By.ID, "refresh")
                refresh_btn.click()
                time.sleep(3)
                
                msgs = self.driver.find_elements(By.CSS_SELECTOR, "#inbox-table tbody tr")
                for msg in msgs:
                    if "ESET" in msg.text:
                        dprint("Found ESET email!")
                        msg.click()
                        time.sleep(2)
                        
                        try:
                            iframe = self.driver.find_element(By.CSS_SELECTOR, "#read iframe")
                            self.driver.switch_to.frame(iframe)
                        except:
                            pass

                        links = self.driver.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            href = link.get_attribute("href")
                            if href and "login.eset.com" in href:
                                dprint(f"Found verification link: {href}")
                                self.driver.get(href)
                                return True
                        
                        self.driver.switch_to.default_content()
            except Exception as e:
                dprint(f"Error checking inbox: {e}")
            
            time.sleep(5)
        return False

    def activate_account(self):
        dprint("Activating account...")
        time.sleep(5) 
        
        try:
            cookie_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "cc-accept"))
            )
            cookie_btn.click()
            dprint("Accepted cookies")
        except:
            pass

        # Check for Re-Login
        try:
            pass_inputs = self.driver.find_elements(By.ID, "password")
            if pass_inputs:
                dprint("Re-login required!")
                try:
                    email_in = self.driver.find_element(By.ID, "email")
                    if not email_in.get_attribute("value"):
                        email_in.send_keys(self.email)
                    
                    pass_in = pass_inputs[0]
                    pass_in.send_keys(self.password)
                    
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-label='browser-log-in-button']")
                    login_btn.click()
                    dprint("Clicked Login")
                    time.sleep(5)
                except Exception as e:
                    dprint(f"Re-login failed: {e}")
        except:
            pass

        # 1. Skip Intro
        try:
            skip_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='onboarding-welcome-skip-introduction-btn']"))
            )
            skip_btn.click()
            dprint("Clicked Skip")
        except:
            dprint("Skip button not found (already skipped?)")

        time.sleep(3)

        # 2. Add Subscription (Select Trial)
        try:
            dprint("Selecting Logic: Start Free Trial option...")
            try:
                trial_label = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='trial']"))
                )
                trial_label.click()
                dprint("Selected Trial Option")
                time.sleep(1)
            except:
                dprint("Trial option not found, maybe already active?")
            
            continue_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue') or contains(., 'Продолжить') or contains(., 'Продовжити')]"))
            )
            continue_btn.click()
            dprint("Clicked Continue (1)")

        except Exception as e:
            dprint(f"Failed in Trial Selection step (non-critical if re-running): {e}")

        time.sleep(3)

        # 3. Select Protection Type (Home usually)
        try:
            dprint("Selecting Protection Type: Home...")
            home_label = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Home') or contains(text(), 'Защита для дома') or contains(text(), 'doma')]/ancestor::label"))
            )
            home_label.click()
            dprint("Selected Home Protection")
            time.sleep(1)

            continue_btn_2 = WebDriverWait(self.driver, 5).until(
                 EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue') or contains(., 'Продолжить') or contains(., 'Продовжити')]"))
            )
            continue_btn_2.click()
            dprint("Clicked Continue (2)")

        except Exception as e:
            dprint(f"Protection Type selection skipped: {e}")

        time.sleep(3)

        # 4. Activation Success Screen -> Click Continue
        try:
            dprint("Checking for Activation Success...")
            continue_btn_3 = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue') or contains(., 'Продолжить') or contains(., 'Продовжити')]"))
            )
            continue_btn_3.click()
            dprint("Clicked Continue (3) - Post Activation")
        except Exception as e:
            dprint(f"Post Activation Continue not found: {e}")

        time.sleep(3)

        # 5. Enter Name Screen
        try:
            dprint("Enter Name Screen...")
            name_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "name"))
            )
            name_input.clear()
            name_input.send_keys(self.full_name) # Random Name
            dprint(f"Filled Name: {self.full_name}")
            
            continue_btn_4 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue') or contains(., 'Продолжить') or contains(., 'Продовжити')]"))
            )
            continue_btn_4.click()
            dprint("Clicked Continue (4) - Name Submitted")

        except Exception as e:
             dprint(f"Name entry skipped or failed: {e}")

        time.sleep(3)

        # 6. "You added yourself" Confirmation Screen
        try:
            dprint("Checking for 'You added yourself' screen...")
            continue_btn_5 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='onboarding-members-continue-btn']"))
            )
            continue_btn_5.click()
            dprint("Clicked Continue (5) - Member Added Confirmation")
        except Exception as e:
             dprint(f"Member confirmation skipped or failed: {e}")

        time.sleep(3)

        # 7. "Who will use" Screen
        try:
            dprint("Checking for 'Who will use' screen...")
            me_option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "label[data-label='onboarding-members-me-option']"))
            )
            me_option.click()
            dprint("Selected 'Only me'")
            time.sleep(1)

            continue_btn_6 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='onboarding-members-continue-btn']"))
            )
            continue_btn_6.click()
            dprint("Clicked Continue (6) - 'Who will use' Confirmation")
        except Exception as e:
             dprint(f"'Who will use' screen skipped or failed: {e}")

        time.sleep(3)

        # 8. "Protect Device" Screen -> Click Finish
        try:
            dprint("Checking for 'Protect Device' screen...")
            finish_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Finish') or contains(., 'Завершить') or contains(., 'Продовжити')]"))
            )
            finish_btn.click()
            dprint("Clicked Finish (7) - Wizard Complete")
        except Exception as e:
             dprint(f"Finish button skipped or failed: {e}")
            
        time.sleep(5)
        
        # 9. Get Key Logic
        try:
            dprint("Entering Key Extraction Phase...")
            
            # Step 1: Click the Subscription Card to go to detail view
            dprint("Looking for Subscription Card...")
            try:
                card_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='dashboard-subscriptions-card-button']"))
                )
                card_btn.click()
                dprint("Clicked Subscription Card")
            except Exception as e:
                dprint(f"Subscription Card not found: {e}")
                
            time.sleep(5)

            # Step 2: Click "Open subscription" button in detail view
            dprint("Looking for 'Open subscription' button...")
            try:
                open_sub_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-label='license-list-open-detail-page-btn']"))
                )
                open_sub_btn.click()
                dprint("Clicked 'Open subscription' button")
                time.sleep(5) 
            except Exception as e:
                dprint(f"'Open subscription' button not found: {e}")

            dprint("Scanning page for license key...")
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Pattern for XXXX-XXXX-XXXX-XXXX-XXXX
            match = re.search(r"([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})", page_text)
            if match:
                key = match.group(1)
                dprint(f"\n!!! FOUND KEY: {key} !!!\n")
                
                # SAVE CREDENTIALS AND KEY TO FILE
                with open("eset_key.txt", "a", encoding="utf-8") as f: # Append mode "a"
                    f.write(f"Email: {self.email} | Password: {self.password} | Name: {self.full_name} | Key: {key}\n")
                    dprint("Saved account info and key to eset_key.txt")
                    
            else:
                dprint("Key not found in text. Dumping HTML...")
                with open("eset_dashboard_final_v7_dump.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                 
        except Exception as e:
            dprint(f"Error extracting key: {e}")

    def run(self):
        try:
            if not self.get_temp_email():
                return
            
            if not self.register_eset_step1():
                return
                
            self.register_eset_step2()
            
            dprint("Attempting to check email automatically...")
            if self.check_email_verification():
                self.activate_account()
            
            dprint("Script finished. Press Enter to close.")
        finally:
            pass

if __name__ == "__main__":
    bot = EsetRegister()
    bot.run()
