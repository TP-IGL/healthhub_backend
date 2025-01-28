from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import time
import random
import string
import argparse

def generate_random_string(length):
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters, k=length))

def generate_random_digits(length):
    """Generate a random string of digits of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def main(login_username, login_password):
    driver = webdriver.Firefox()
    try:
        # Navigate to login page
        print("Navigating to login page...")
        driver.get("http://localhost:4200/")
        driver.maximize_window()
        time.sleep(2)

        # Login with provided credentials
        print(f"Performing login with username: {login_username}")
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = driver.find_element(By.ID, "password")
        
        username_input.clear()
        username_input.send_keys(login_username)
        password_input.clear()
        password_input.send_keys(login_password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Rest of the test script remains the same...
        print("Waiting for dashboard...")
        time.sleep(2)
        add_patient_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Ajouter patient')]"))
        )
        add_patient_button.click()

        form_fields = {
            "username": f"test_user_{generate_random_string(3)}", 
            "email": f"test{random.randint(1,1000)}@example.com",
            "password": "password123",
            "NSS": generate_random_digits(10),
            "nom": f"Doe_{generate_random_string(2)}",
            "prenom": f"John_{generate_random_string(2)}",
            "dateNaissance": "2000-01-01",
            "adresse": f"{generate_random_digits(3)} Main Street",
            "telephone": generate_random_digits(10),
            "mutuelle": "Mutuelle Test",
            "contactUrgence": generate_random_digits(10),
            "centreHospitalier": "1"
        }

        print("\nFilling out form with validated data...")
        for field_id, value in form_fields.items():
            try:
                field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, field_id))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", field)
                field.clear()
                field.send_keys(value)
                print(f"Filled {field_id}: {value}")
            except Exception as e:
                print(f"Error filling {field_id}: {str(e)}")
                raise

        print("\nSelecting médecin...")
        try:
            medecin_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "medecin"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", medecin_select)
            select = Select(medecin_select)
            select.select_by_value("b35d8481-f50c-442e-8717-9b75a4a84973")
            print("Médecin selected successfully")
        except Exception as e:
            print(f"Warning - médecin selection failed: {str(e)}")
            print("Continuing as médecin is nullable...")

        print("\nSubmitting form...")
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()

        try:
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"\nValidation alert detected: {alert_text}")
            alert.accept()
            print("Test failed: Form validation error")
            print("\nCurrent field values:")
            for field_id, value in form_fields.items():
                print(f"{field_id}: {value}")
            raise Exception("Form validation failed")
        except TimeoutException:
            print("No validation alerts detected - continuing...")

        print("\nWaiting for redirect to dashboard...")
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: driver.current_url == "http://localhost:4200/dashboard"
            )
            print("Test passed: Patient created successfully! (Redirected to dashboard)")
        except TimeoutException:
            print(f"Test failed: Not redirected to dashboard. Current URL: {driver.current_url}")
            raise Exception("Redirect to dashboard failed")

    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        driver.save_screenshot(f"error_screenshot_{timestamp}.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run patient creation test with specific login credentials')
    parser.add_argument('username', help='Username for login')
    parser.add_argument('password', help='Password for login')
    
    args = parser.parse_args()
    main(args.username, args.password)