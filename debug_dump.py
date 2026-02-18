
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def dump_html():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    # Mohmal
    print("Navigating to Mohmal...")
    driver.get("https://www.mohmal.com/en")
    time.sleep(5) # Wait for load
    with open("mohmal_dump.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Dumped mohmal_dump.html")

    # ESET
    print("Navigating to ESET...")
    driver.get("https://login.eset.com/register/index")
    time.sleep(5)
    with open("eset_dump.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Dumped eset_dump.html")

    driver.quit()

if __name__ == "__main__":
    dump_html()
