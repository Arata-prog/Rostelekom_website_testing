import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


ROSTELECOM_LOGIN_URL = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid'
ROSTELECOM_ORDER_URL = 'https://lk.rt.ru/#service-ordering'
ROSTELECOM_LK_MAIN_URL = 'https://lk.rt.ru/#'
RELOCATION_STEP0_URL = 'https://start.rt.ru/pereezd/steps?step=0'


VALID_EMAIL = "leo.watch@mail.ru"
VALID_PASSWORD_FOR_EMAIL = "Awsed@1524&"


CONTACT_NAME = "Тест Тестович"
INVALID_CONTACT_NAME = CONTACT_NAME + " 111"
CONTACT_PHONE = "9991234567"
ORDER_REGION = "Республика Саха (Якутия)"
ORDER_CITY = "Якутск"
ORDER_STREET = "Ленина"
ORDER_HOUSE = "1"
ORDER_APARTMENT = "1"
SUPPORT_MESSAGE = "помогите"
RELOCATION_PHONE = "9991234567"
INVALID_REGION = "111111111111"
EXPECTED_REGION_ERROR = "Выберите значение из списка"
EXPECTED_PHONE_ERROR = "Некорректный номер"
EXPECTED_NAME_ERROR_TEXT = "Фамилия и имя должны состоять из русских букв через пробел. Допускается использовать дефиc."


@pytest.fixture(scope="function")
def driver():
    """Инициализирует драйвер Firefox и выполняет вход в ЛК."""
    firefox_options = Options()
    firefox_options.add_argument("--start-maximized")
    driver_instance = None
    try:
        driver_instance = webdriver.Firefox(options=firefox_options)
        wait = WebDriverWait(driver_instance, 20)
        driver_instance.get(ROSTELECOM_LOGIN_URL)
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        
        email_tab = driver_instance.find_element(By.ID, "t-btn-tab-mail")
        if email_tab.get_attribute("aria-selected") != 'true':
            email_tab.click()
            time.sleep(0.3)

        username_field = driver_instance.find_element(By.ID, "username")
        password_field = driver_instance.find_element(By.ID, "password")
        login_button = driver_instance.find_element(By.ID, "kc-login")

        username_field.clear()
        username_field.send_keys(VALID_EMAIL)
        password_field.clear()
        password_field.send_keys(VALID_PASSWORD_FOR_EMAIL)

        initial_url = driver_instance.current_url
        login_button.click()

        WebDriverWait(driver_instance, 60).until(EC.url_changes(initial_url))
        assert "/auth/" not in driver_instance.current_url, "Не удалось покинуть страницу аутентификации после входа."

    except Exception as e:
        print(f"Критическая ошибка в фикстуре 'driver': {str(e)}")
        if driver_instance:
            try:
                driver_instance.save_screenshot("fixture_critical_error.png")
            except: 
                pass
            driver_instance.quit()
        pytest.fail(f"Ошибка в фикстуре 'driver': {e}")

    yield driver_instance

    if driver_instance:
        driver_instance.quit()

def test_service_order_invalid_name(driver):
    """Тест: Ввод невалидного имени и проверка сообщения об ошибке."""
    wait = WebDriverWait(driver, 30)

    form_container_css = ".service-ordering_address-selector"
    name_field_xpath = "//input[@id=(//label[text()='Фамилия Имя']/@for)]"
    phone_field_xpath = "//input[@id=(//label[text()='Контактный телефон']/@for)]"
    name_error_message_css = "div.error-message--input"
    
    try:
        driver.get(ROSTELECOM_ORDER_URL)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, form_container_css)))

        name_field = wait.until(EC.element_to_be_clickable((By.XPATH, name_field_xpath)))
        name_field.clear()
        name_field.send_keys(INVALID_CONTACT_NAME)

        wait.until(EC.element_to_be_clickable((By.XPATH, phone_field_xpath))).click()
        time.sleep(0.5)

        error_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, name_error_message_css)))
        assert error_element.text == EXPECTED_NAME_ERROR_TEXT, f"Ожидался текст ошибки: '{EXPECTED_NAME_ERROR_TEXT}', получено: '{error_element.text}'"

    except Exception as e:
        pytest.fail(f"Ошибка в test_service_order_invalid_name: {e}")


def test_support_chat_widget(driver):
    """Тест: Открытие чата поддержки и отправка сообщения."""
    wait = WebDriverWait(driver, 60)

    chat_widget_button_xpath = "//div[normalize-space()='Поддержка' and contains(@class, 'omnichat-text')]"
    chat_input_css = "textarea[data-testid='text-field']"
    chat_send_button_id = "widget_push-message"

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, chat_widget_button_xpath))).click()
        
        chat_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, chat_input_css)))
        chat_input.clear()
        chat_input.send_keys(SUPPORT_MESSAGE)
        
        wait.until(EC.element_to_be_clickable((By.ID, chat_send_button_id))).click()

    except Exception as e:
        pytest.fail(f"Ошибка в test_support_chat_widget: {e}")


def test_vk_link(driver):
    """Тест: Клик по ссылке VK открывает новую вкладку."""
    wait = WebDriverWait(driver, 30)
    
    vk_link_css = "a[title='вконтакте']"

    try:
        initial_window_handle = driver.current_window_handle
        initial_window_handles = driver.window_handles
        
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, vk_link_css))).click()
        
        wait.until(EC.number_of_windows_to_be(len(initial_window_handles) + 1))
        new_window_handle = [h for h in driver.window_handles if h not in initial_window_handles][0]
        driver.switch_to.window(new_window_handle)
        
        wait.until(EC.url_contains("vk.com"))
        assert "vk.com" in driver.current_url, "URL новой вкладки не содержит vk.com"
        
        driver.close()
        driver.switch_to.window(initial_window_handle)
        assert len(driver.window_handles) == len(initial_window_handles), "Количество вкладок не вернулось к исходному"

    except Exception as e:
        driver.save_screenshot("test_vk_link_error.png")
        pytest.fail(f"Ошибка в test_vk_link: {e}")


def test_relocation_form_phone(driver):
    """Тест: Ввод региона и номера телефона на форме Переезда."""
    wait = WebDriverWait(driver, 60)

    region_input_css = "input[name='region']"
    region_suggestion_xpath = f"//span[contains(@class, 'Label-idpbLq')][normalize-space()='{ORDER_REGION}']"
    phone_input_css = "input[name='phone']"
    confirm_button_xpath = "//button[normalize-space()='Подтвердить номер']"
    code_sent_text_xpath = "//p[normalize-space()='Код подтверждения отправлен']"

    try:
        driver.get(RELOCATION_STEP0_URL)

        region_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, region_input_css)))
        region_input.clear()
        region_input.send_keys(ORDER_REGION)
        time.sleep(3)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, region_input_css))).click()
        time.sleep(0.5)
        wait.until(EC.visibility_of_element_located((By.XPATH, region_suggestion_xpath)))
        region_suggestion = wait.until(EC.element_to_be_clickable((By.XPATH, region_suggestion_xpath)))
        driver.execute_script("arguments[0].click();", region_suggestion)
        time.sleep(0.3)
        
        phone_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, phone_input_css)))
        phone_input.clear()
        phone_input.send_keys(RELOCATION_PHONE)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))).click()
        
        confirmation_text = wait.until(EC.visibility_of_element_located((By.XPATH, code_sent_text_xpath)))
        assert confirmation_text is not None, "Текст подтверждения отправки кода не найден"

    except Exception as e:
        pytest.fail(f"Ошибка в test_relocation_form_phone: {e}")


def test_relocation_invalid_region(driver):
    """Тест: Ввод невалидного региона и проверка ошибки."""
    wait = WebDriverWait(driver, 30)

    region_input_css = "input[name='region']"
    phone_input_css = "input[name='phone']"
    region_error_css = "p.Error-heguQr"

    try:
        driver.get(RELOCATION_STEP0_URL)
        
        region_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, region_input_css)))
        region_input.clear()
        region_input.send_keys(INVALID_REGION)
        
        phone_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, phone_input_css)))
        phone_input.clear()
        phone_input.send_keys(RELOCATION_PHONE)
        
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.5)
        
        error_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, region_error_css)))
        assert error_element.text == EXPECTED_REGION_ERROR, f"Ожидался текст ошибки: '{EXPECTED_REGION_ERROR}', получено: '{error_element.text}'"

    except Exception as e:
        pytest.fail(f"Ошибка в test_relocation_invalid_region: {e}")


def test_relocation_empty_phone(driver):
    """Тест: Пустое поле телефона и проверка ошибки."""
    wait = WebDriverWait(driver, 60)
    
    region_input_css = "input[name='region']"
    region_suggestion_xpath = f"//span[contains(@class, 'Label-idpbLq')][normalize-space()='{ORDER_REGION}']"
    phone_input_css = "input[name='phone']"
    phone_error_css = "p.Error-heguQr"

    try:
        driver.get(RELOCATION_STEP0_URL)
        
        region_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, region_input_css)))
        region_input.clear()
        region_input.send_keys(ORDER_REGION)
        time.sleep(3)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, region_input_css))).click()
        time.sleep(0.5)
        wait.until(EC.visibility_of_element_located((By.XPATH, region_suggestion_xpath)))
        region_suggestion = wait.until(EC.element_to_be_clickable((By.XPATH, region_suggestion_xpath)))
        driver.execute_script("arguments[0].click();", region_suggestion)
        time.sleep(0.3)

        phone_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, phone_input_css)))
        phone_input.click()
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.5)
        
        error_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, phone_error_css)))
        assert error_element.text == EXPECTED_PHONE_ERROR, f"Ожидался текст ошибки: '{EXPECTED_PHONE_ERROR}', получено: '{error_element.text}'"

    except Exception as e:
        pytest.fail(f"Ошибка в test_relocation_empty_phone: {e}")


def test_service_order_form(driver):
    """Тест заполнения формы заказа услуг."""
    wait = WebDriverWait(driver, 90)
    
    form_container_css = ".service-ordering_address-selector"
    header_to_disappear_xpath = "//header[contains(@class, 'n-header') and normalize-space()='Выберите услуги']"
    internet_service_xpath = "//div[contains(@class, 'service-ordering_switcher_header')][.//h3[normalize-space()='Интернет']]//div[contains(@class, 'switcher')]"
    tv_service_xpath = "//div[contains(@class, 'service-ordering_switcher_header')][.//h3[normalize-space()='Интерактивное ТВ']]//div[contains(@class, 'switcher')]"
    name_field_xpath = "//input[@id=(//label[text()='Фамилия Имя']/@for)]"
    phone_field_xpath = "//input[@id=(//label[text()='Контактный телефон']/@for)]"
    region_dropdown_xpath = "//div[contains(@class, 'combobox')][.//label[text()='Регион оказания услуг']]"
    region_option_xpath = f"//div[contains(@class, 'combobox_dropdown_item')][normalize-space()='{ORDER_REGION}']"
    city_field_xpath = "//input[@id=(//label[text()='Населенный пункт']/@for)]"
    city_suggestion_xpath = f"//div[contains(@class, 'address-selector_input_element')][normalize-space()='{ORDER_CITY}']"
    street_field_xpath = "//input[@id=(//label[text()='Улица']/@for)]"
    street_suggestion_xpath = f"//div[contains(@class, 'address-selector_input_element')][.//div[normalize-space()='ул. {ORDER_STREET}']]"
    house_field_xpath = "//input[@id=(//label[text()='№ дома']/@for)]"
    apartment_field_xpath = "//input[@id=(//label[text()='Квартира']/@for)]"
    continue_button_xpath = "//button[normalize-space()='Продолжить']"

    try:
        driver.get(ROSTELECOM_ORDER_URL)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, form_container_css)))

        wait.until(EC.element_to_be_clickable((By.XPATH, internet_service_xpath))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, tv_service_xpath))).click()

        name_field = wait.until(EC.element_to_be_clickable((By.XPATH, name_field_xpath)))
        name_field.clear()
        name_field.send_keys(CONTACT_NAME)

        phone_field = wait.until(EC.element_to_be_clickable((By.XPATH, phone_field_xpath)))
        phone_field.clear()
        phone_field.send_keys(CONTACT_PHONE)

        wait.until(EC.element_to_be_clickable((By.XPATH, region_dropdown_xpath))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, region_option_xpath))).click()
        
        city_field = wait.until(EC.element_to_be_clickable((By.XPATH, city_field_xpath)))
        city_field.clear()
        city_field.send_keys(ORDER_CITY)
        wait.until(EC.element_to_be_clickable((By.XPATH, city_suggestion_xpath))).click()
        
        street_field = wait.until(EC.element_to_be_clickable((By.XPATH, street_field_xpath)))
        street_field.clear()
        street_field.send_keys(ORDER_STREET)
        wait.until(EC.element_to_be_clickable((By.XPATH, street_suggestion_xpath))).click()
        
        house_field = wait.until(EC.element_to_be_clickable((By.XPATH, house_field_xpath)))
        house_field.clear()
        house_field.send_keys(ORDER_HOUSE)
        
        apartment_field = wait.until(EC.element_to_be_clickable((By.XPATH, apartment_field_xpath)))
        apartment_field.clear()
        apartment_field.send_keys(ORDER_APARTMENT)

        wait.until(EC.element_to_be_clickable((By.XPATH, continue_button_xpath))).click()

        time.sleep(5)
        
        header_disappeared = wait.until_not(EC.visibility_of_element_located((By.XPATH, header_to_disappear_xpath)))
        assert header_disappeared, "Заголовок 'Выберите услуги' не исчез после нажатия кнопки 'Продолжить'"

    except Exception as e:
        pytest.fail(f"Ошибка в test_service_order_form: {e}")

if __name__ == "__main__":
    pytest.main(['-v', __file__])