import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from seleniumide.scheme import SITE_SCHEME


class BaseDriver:
    def __init__(self,
                 base_url: str = "http://refor.detran.rj.gov.br/",
                 chrome_options: webdriver.ChromeOptions = None):

        
        self.URL_BASE = 'http://refor.detran.rj.gov.br/'
        self.chrome_options = Options()
        #self.chrome_options.add_argument('--headless')
        #self.chrome_options.add_argument('--no-sandbox')
        #self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver_path: str = ChromeDriverManager().install()

    def setDriver(self, executable_path, chrome_options):
        self.DRIVER: webdriver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)
        self.DRIVER.set_page_load_timeout(10)
        self.DRIVER.implicitly_wait(10)
    
        self.current_screen = None
        self.current_frame = None
        return self.DRIVER

    def find_element_by_clickable(self, value, by=By.XPATH, retry_count=2, retry_sleep=2) -> WebElement:
        for attempt in range(retry_count):

            erros = ['Disconnect Message', 'Informe a SENHA', 'Script not found']
            if any(t in self.DRIVER.page_source for t in erros):
                raise ValueError('Natural Disconnect')
            try:
                WebDriverWait(self.DRIVER, 5).until(EC.element_to_be_clickable((by, value))).click()
                return self.page_state()
            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                print(f"{by}={value}: Element not found {attempt + 1}/{retry_count}")
                self.page_state()
                time.sleep(retry_sleep)
        raise NoSuchElementException(f"{by}={value}: Element not found")


    def find_element(self, value, by=By.XPATH, retry_count=2, retry_sleep=0.5) -> WebElement:
        for attempt in range(retry_count):
            erros = ['Disconnect Message', 'Informe a SENHA']
            if any(t in self.DRIVER.page_source for t in erros):
                raise ValueError('Natural Disconnect')
            try:
                return self.DRIVER.find_element(by, value)
            except (TimeoutException, StaleElementReferenceException):
                print(f"{by}={value}: Element not found {attempt + 1}/{retry_count}")
                time.sleep(retry_sleep)
        raise NoSuchElementException(f"{by}={value}: Element not found") 

    def find_element_if_visible(self, value, by=By.XPATH, timeout=15) -> WebElement:
        while timeout:
            if self.DRIVER.find_elements(by, value) != []:
                time.sleep(1)
                return self.DRIVER.find_element(by, value)
            timeout -= 1


    def find_locator(self, element: str, screen: str = None, retry_count=2, retry_sleep=0.5, method=None):
        
        screen = screen or self.current_screen

        iframe = SITE_SCHEME[screen]["iframe"]
        self.switch_to_frame(iframe)

        locator = SITE_SCHEME[screen]["elements"][element]
        if method == 'click' or method == 'clear' or method == 'send_keys':
            return self.find_element_by_clickable(locator, by=By.XPATH, retry_count=retry_count, retry_sleep=retry_sleep)
        
        if method == "visible":
            self.find_element_if_visible(locator, by=By.XPATH)

        return self.find_element(locator, by=By.XPATH, retry_count=retry_count, retry_sleep=retry_sleep)

    def switch_to_default_content(self):
        if self.current_frame is None:
            return
        self.DRIVER.switch_to.default_content()
        self.current_frame = None

    def switch_to_frame(self, value, retry_count=3, retry_sleep=0.5):
        if self.current_frame == value:
            return
        self.switch_to_default_content()
        self.find_element(value, By.ID, retry_count=retry_count, retry_sleep=retry_sleep)
        self.DRIVER.switch_to.frame(value)
        self.current_frame = value

    def switch_to_screen(self, screen: str):
        if screen in SITE_SCHEME:
            self.switch_to_frame(SITE_SCHEME[screen]["iframe"])
            self.current_screen = screen
        else:
            raise Exception(f"Screen {screen} not found")

    def page_state(self, timeout=1000, implicitlyWait=time.sleep(0.1)):
        last_current_frame = self.current_screen
        self.switch_to_default_content()
        while timeout:
            frame = self.DRIVER.execute_script('return document.getElementById("WA1").contentDocument.body.outerHTML;')
            soap = BeautifulSoup(frame, 'html.parser')
            hourglass = soap.find('div', {'id': 'THISOCCUPIED'})['style']

            if 'display: none;' not in hourglass:
                implicitlyWait
                timeout -= 1
            else:
                time.sleep(1)
                return self.switch_to_screen(last_current_frame)
                

    @staticmethod
    def screen_decorator(screen: str):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self.current_screen != screen:
                    raise Exception(f"Need to be on {screen} screen: {self.current_screen}")
                return func(self, *args, **kwargs)

            return wrapper

        return decorator
