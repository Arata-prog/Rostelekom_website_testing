import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

ROSTELECOM_LOGIN_URL = 'https://b2c.passport.rt.ru/auth/realms/b2c/protocol/openid-connect/auth?client_id=account_b2c&redirect_uri=https://b2c.passport.rt.ru/account_b2c/login&response_type=code&scope=openid&state=b3966cbb-9d0e-4cb5-a4ec-c7ee344c67ab'

VALID_EMAIL = "leo.watch@mail.ru"
VALID_PASSWORD_FOR_EMAIL = "Awsed@1524&"

VALID_LOGIN = "leo.watch@mail.ru"
VALID_PASSWORD_FOR_LOGIN = "Awsed@1524&"

# Невалидные данные
INVALID_USERNAME = "invalid_user"
INVALID_PASSWORD = "invalid_pass"

@pytest.fixture(autouse=True)
def driver():
    """Инициализирует драйвер Firefox и открывает страницу входа."""
    firefox_options = Options()
    firefox_options.add_argument("--start-maximized")

    driver_instance = None
    try:
        driver_instance = webdriver.Firefox(options=firefox_options)
        driver_instance.get(ROSTELECOM_LOGIN_URL)
        wait = WebDriverWait(driver_instance, 15)
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
    except Exception as e:
        print(f"Ошибка при настройке драйвера или навигации: {str(e)}")
        if driver_instance:
            driver_instance.quit()
        raise

    yield driver_instance

    if driver_instance:
        driver_instance.quit()


def test_successful_email(driver):
   """Тест успешного входа с валидными EMAIL и паролем."""
   wait = WebDriverWait(driver, 90)

   try:
       email_tab = driver.find_element(By.ID, "t-btn-tab-mail")
       email_tab.click()
       time.sleep(0.5)

       username_field = driver.find_element(By.ID, "username")
       password_field = driver.find_element(By.ID, "password")
       login_button = driver.find_element(By.ID, "kc-login")

       username_field.clear()
       username_field.send_keys(VALID_EMAIL)
       password_field.clear()
       password_field.send_keys(VALID_PASSWORD_FOR_EMAIL)

       initial_url = driver.current_url
       login_button.click()

       wait.until(EC.url_changes(initial_url))
       new_url = driver.current_url
       assert "/auth/" not in new_url, "URL после входа все еще содержит /auth/"

   except TimeoutException:
        pytest.fail("URL не изменился после попытки входа по email.")
   except Exception as e:
       pytest.fail(f"Тест test_successful_email не пройден: {e}")


def test_successful_login(driver):
   """Тест успешного входа с валидными ЛОГИНОМ и паролем."""
   wait = WebDriverWait(driver, 15)

   try:
       login_tab = driver.find_element(By.ID, "t-btn-tab-login")
       login_tab.click()
       time.sleep(0.5)

       username_field = driver.find_element(By.ID, "username")
       password_field = driver.find_element(By.ID, "password")
       login_button = driver.find_element(By.ID, "kc-login")

       username_field.clear()
       username_field.send_keys(VALID_LOGIN)
       password_field.clear()
       password_field.send_keys(VALID_PASSWORD_FOR_LOGIN)

       initial_url = driver.current_url
       login_button.click()

       wait.until(EC.url_changes(initial_url))
       new_url = driver.current_url
       assert "/auth/" not in new_url, "URL после входа все еще содержит /auth/"

   except TimeoutException:
        pytest.fail("URL не изменился после попытки входа по логину.")
   except Exception as e:
       pytest.fail(f"Тест test_successful_login не пройден: {e}")


def test_failed_login(driver):
    """Тест неуспешного входа с невалидными данными."""
    wait = WebDriverWait(driver, 10)

    try:
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "kc-login")

        username_field.clear()
        username_field.send_keys(INVALID_USERNAME)
        password_field.clear()
        password_field.send_keys(INVALID_PASSWORD)

        login_button.click()

        error_message_selector = (By.ID, "form-error-message")
        error_element = wait.until(EC.visibility_of_element_located(error_message_selector))
        assert error_element.is_displayed(), "Сообщение об ошибке не отображается"

        expected_error_text = "Неверный логин или пароль"
        assert expected_error_text in error_element.text, f"Некорректный текст ошибки. Ожидалось '{expected_error_text}', получено: '{error_element.text}'"

    except TimeoutException:
        pytest.fail(f"Не удалось найти сообщение об ошибке ({error_message_selector[1]}) после ввода невалидных данных.")
    except Exception as e:
        pytest.fail(f"Тест test_failed_login не пройден: {e}")


def test_vk_social_login(driver):
    """Тест проверяет редирект на страницу VK ID."""
    wait = WebDriverWait(driver, 15)

    try:
        vk_button = driver.find_element(By.ID, "oidc_vk")
        vk_button.click()

        wait.until(EC.url_contains("id.vk.com"))
        current_url = driver.current_url
        assert "id.vk.com" in current_url, f"URL после редиректа ({current_url}) не содержит 'id.vk.com'"

    except TimeoutException:
        pytest.fail("Не дождались редиректа на URL, содержащий 'id.vk.com'.")
    except Exception as e:
        pytest.fail(f"Тест test_vk_social_login не пройден: {e}")


def test_user_agreement(driver):
    """Тест проверяет, что ссылка 'пользовательского соглашения' открывается в новой вкладке."""
    wait = WebDriverWait(driver, 15)

    initial_window_handle = driver.current_window_handle
    initial_window_handles = driver.window_handles

    try:
        agreement_link = driver.find_element(By.ID, "rt-auth-agreement-link")
        expected_url = "https://b2c.passport.rt.ru/sso-static/agreement/agreement.html"
        agreement_link.click()

        wait.until(EC.number_of_windows_to_be(len(initial_window_handles) + 1))

        new_window_handle = [handle for handle in driver.window_handles if handle not in initial_window_handles][0]
        driver.switch_to.window(new_window_handle)

        wait.until(EC.url_to_be(expected_url))
        current_url = driver.current_url
        assert current_url == expected_url, f"URL новой вкладки ({current_url}) не совпадает с ожидаемым ({expected_url})"

        driver.close()
        driver.switch_to.window(initial_window_handle)
        assert len(driver.window_handles) == len(initial_window_handles), "Количество вкладок не вернулось к исходному"

    except TimeoutException:
        pytest.fail("Не дождались открытия новой вкладки или загрузки ожидаемого URL в ней.")
    except Exception as e:
        pytest.fail(f"Тест test_user_agreement не пройден: {e}")

if __name__ == "__main__":
    pytest.main(['-v', __file__])