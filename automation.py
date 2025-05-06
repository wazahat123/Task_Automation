import sys
import pandas as pd
import os
import time
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Get Excel File Path from Command Line Arguments ---
excel_file = sys.argv[1]

if not os.path.exists(excel_file):
    raise FileNotFoundError(f"Excel file not found: {excel_file}")

df = pd.read_excel(excel_file)
if df.empty:
    raise ValueError(f"The Excel file '{excel_file}' is empty or could not be loaded properly.")

# --- Setup Chrome Driver (Linux + Headless) ---
chrome_driver_path = "/usr/bin/chromedriver"  # Linux typical path (update if needed)

if not os.path.exists(chrome_driver_path):
    raise FileNotFoundError(f"ChromeDriver not found at {chrome_driver_path}")

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
wait = WebDriverWait(driver, 30)

# --- Login ---
driver.get("https://cms.selectyouruniversity.com/admin/login")
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("arsh.dm@syu.com")
wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("Arsh@123", Keys.RETURN)
time.sleep(2)

# --- Navigate to Tasks Section ---
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-toggler']/button"))).click()
time.sleep(2)
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-tasks']/span[2]"))).click()
time.sleep(2)
wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div[2]/div/div/header/div/button/span"))).click()
time.sleep(2)

# --- Process Each Task ---
df.columns = df.columns.str.strip()
filtered_df = df[df['title'].notna() & (df['title'].astype(str).str.strip() != '')]

for index, row in filtered_df.iterrows():
    task_name = str(row.get("title", "")).strip()
    description_value = str(row.get("description", "")).strip()
    data_manager_value = str(row.get("Data Manager", "")).strip()
    data_entry_operator_value = str(row.get("Data Entry Operator", "")).strip()
    entity_value = str(row.get("Entity", "")).strip()
    task_date = str(row.get("date", "")).strip()

    print(f"🔄 Processing Task {index + 1}: {task_name}")

    try:
        # Fill form fields (same logic as before)

        title_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div[2]/div/form/div[4]/div/div[1]/div/div[2]/div/div[2]/input")))
        driver.execute_script("arguments[0].scrollIntoView(true);", title_input)
        title_input.clear()
        title_input.send_keys(task_name)

        description_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/form/div[4]/div/div[1]/div/div[3]/div/div[2]/textarea')))
        driver.execute_script("arguments[0].scrollIntoView(true);", description_input)
        description_input.clear()
        description_input.send_keys(description_value)

        category_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='syuSelect-:r7:']/div/div[1]/div")))
        driver.execute_script("arguments[0].scrollIntoView(true);", category_dropdown)
        category_dropdown.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Colleges')]"))).click()

        update_toggle = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div/form/div[4]/div/div[1]/div/div[6]/div/div/label/div[1]')))
        driver.execute_script("arguments[0].scrollIntoView(true);", update_toggle)
        driver.execute_script("arguments[0].click();", update_toggle)

        # Handle Due Date
        task_date = parser.parse(task_date) if isinstance(task_date, str) else pd.to_datetime(task_date)
        day, month, year = str(task_date.day).zfill(2), str(task_date.month).zfill(2), str(task_date.year)
        day_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div/input[2]')))
        month_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div/input[3]')))
        year_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/form/div[4]/div/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div/input[4]')))
        for input_field, value in zip([day_input, month_input, year_input], [day, month, year]):
            driver.execute_script("arguments[0].scrollIntoView(true);", input_field)
            input_field.clear()
            input_field.send_keys(value)

        # Data Manager
        dm_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Data Manager')]/following::input[1]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", dm_input)
        dm_input.clear()
        dm_input.send_keys(data_manager_value)
        time.sleep(1)
        dm_input.send_keys(Keys.ENTER)

        # Data Entry Operator
        deo_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Data Entry Operator')]/following::input[1]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", deo_input)
        deo_input.clear()
        deo_input.send_keys(data_entry_operator_value)
        time.sleep(1)
        deo_input.send_keys(Keys.ENTER)

        # Entity
        entity_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Entity')]/following::input[1]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", entity_input)
        entity_input.clear()
        entity_input.send_keys(entity_value)
        time.sleep(1)
        entity_input.send_keys(Keys.ENTER)

        # Submit
        submit_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div[2]/div/form/div[3]/div[2]/button")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
        time.sleep(1)
        submit_button.click()

        print(f"✅ Task {index + 1} submitted successfully!")
        time.sleep(3)
        driver.refresh()
        time.sleep(5)

        add_new_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/div[2]/div/div/header/div/button/span")))
        add_new_btn.click()
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error in Task {index + 1}: {e}")
        continue

print("🎉 All tasks processed and submitted.")
driver.quit()
