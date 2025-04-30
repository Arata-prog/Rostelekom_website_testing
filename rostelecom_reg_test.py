import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

ROSTELECOM_BASE_URL = 'https://b2c.passport.rt.ru/'

FIRST_NAME = "Иван"
LAST_NAME = "Тестов"
REGION = "Москва г" 
NEW_EMAIL = "testsimple9876543210@testrt.ru" 
PASSWORD = "PassWord123!"

INVALID_NAME_DIGITS = "12345"
INVALID_PASSWORD_NO_CAPITAL = "password123!"
INVALID_PASSWORD_CONFIRM = "Different123!"
EXISTING_EMAIL = "leo.watch@mail.ru"

ERROR_MSG_CLASS = "rt-input-container__meta--error"

@pytest.fixture(scope="function")
def driver():
    """Инициализирует драйвер и переходит на страницу регистрации."""
    firefox_options = Options()
    firefox_options.add_argument("--start-maximized")
    driver_instance = None
    try:
        driver_instance = webdriver.Firefox(options=firefox_options)
        driver_instance.get(ROSTELECOM_BASE_URL)
        wait = WebDriverWait(driver_instance, 15)
        register_link = wait.until(EC.element_to_be_clickable((By.ID, "kc-register")))
        register_link.click()
        wait.until(EC.text_to_be_present_in_element((By.ID, 'card-title'), "Регистрация"))
    except Exception as e:
        print(f"Критическая ошибка при настройке драйвера или навигации: {str(e)}")
        if driver_instance:
            driver_instance.quit()
        pytest.fail(f"Не удалось инициализировать и перейти к регистрации: {e}")

    yield driver_instance

    if driver_instance:
        driver_instance.quit()


def test_registration_invalid_firstname(driver):
    """Тест: Имя содержит цифры (проверяем наличие ЛЮБОЙ ошибки)."""
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.NAME, "firstName").send_keys(INVALID_NAME_DIGITS)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)

   
    driver.find_element(By.CLASS_NAME, "rt-select__rt-input").click()

    region_option_xpath = f"//div[@class='rt-select__list-item'][normalize-space()='{REGION}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
    time.sleep(0.5) 

    driver.find_element(By.ID, "address").send_keys(NEW_EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password-confirm").send_keys(PASSWORD)

    driver.find_element(By.NAME, "register").click()

    error_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, ERROR_MSG_CLASS)))
    assert error_element is not None 

def test_registration_missing_region(driver):
    """Тест: Регион не выбран (проверяем наличие ЛЮБОЙ ошибки)."""
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.NAME, "firstName").send_keys(FIRST_NAME)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)
    driver.find_element(By.ID, "address").send_keys(NEW_EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password-confirm").send_keys(PASSWORD)

    driver.find_element(By.NAME, "register").click()

    error_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, ERROR_MSG_CLASS)))
    assert error_element is not None

def test_registration_existing_account(driver):
    """Тест: Email уже зарегистрирован."""
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.NAME, "firstName").send_keys(FIRST_NAME)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)
    driver.find_element(By.CLASS_NAME, "rt-select__rt-input").click()
    region_option_xpath = f"//div[@class='rt-select__list-item'][normalize-space()='{REGION}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
    time.sleep(0.5)
    driver.find_element(By.ID, "address").send_keys(EXISTING_EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password-confirm").send_keys(PASSWORD)

    driver.find_element(By.NAME, "register").click()

    modal_title = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "card-modal__title")))
    assert modal_title.text == "Учётная запись уже существует"

def test_registration_invalid_password_format(driver):
    """Тест: Пароль без заглавной буквы (проверяем наличие ЛЮБОЙ ошибки)."""
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.NAME, "firstName").send_keys(FIRST_NAME)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)
    driver.find_element(By.CLASS_NAME, "rt-select__rt-input").click()
    region_option_xpath = f"//div[@class='rt-select__list-item'][normalize-space()='{REGION}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
    time.sleep(0.5)
    driver.find_element(By.ID, "address").send_keys(NEW_EMAIL)
    driver.find_element(By.ID, "password").send_keys(INVALID_PASSWORD_NO_CAPITAL)
    driver.find_element(By.ID, "password-confirm").send_keys(INVALID_PASSWORD_NO_CAPITAL)

    driver.find_element(By.NAME, "register").click()

    error_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, ERROR_MSG_CLASS)))
    assert error_element is not None

def test_registration_password_mismatch(driver):
    """Тест: Пароли не совпадают (проверяем наличие ЛЮБОЙ ошибки)."""
    wait = WebDriverWait(driver, 10)

    driver.find_element(By.NAME, "firstName").send_keys(FIRST_NAME)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)
    driver.find_element(By.CLASS_NAME, "rt-select__rt-input").click()
    region_option_xpath = f"//div[@class='rt-select__list-item'][normalize-space()='{REGION}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
    time.sleep(0.5)
    driver.find_element(By.ID, "address").send_keys(NEW_EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password-confirm").send_keys(INVALID_PASSWORD_CONFIRM)

    driver.find_element(By.NAME, "register").click()

    error_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, ERROR_MSG_CLASS)))
    assert error_element is not None

def test_registration_success_attempt(driver):
    """Тест: Успешная попытка регистрации (переход к подтверждению)."""
    wait = WebDriverWait(driver, 15) 

    driver.find_element(By.NAME, "firstName").send_keys(FIRST_NAME)
    driver.find_element(By.NAME, "lastName").send_keys(LAST_NAME)
    driver.find_element(By.CLASS_NAME, "rt-select__rt-input").click()
    region_option_xpath = f"//div[@class='rt-select__list-item'][normalize-space()='{REGION}']"
    wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
    time.sleep(0.5)
    driver.find_element(By.ID, "address").send_keys(NEW_EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "password-confirm").send_keys(PASSWORD)

    driver.find_element(By.NAME, "register").click()

    confirm_title = wait.until(EC.visibility_of_element_located((By.ID, "card-title")))
    assert "Подтверждение" in confirm_title.text

if __name__ == "__main__":
    pytest.main(['-v', __file__]) 