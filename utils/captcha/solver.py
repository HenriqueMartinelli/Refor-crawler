import json
import time
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from seleniumide.init import BaseDriver
from utils.captcha.answers import CAPTCHA_ANSWERS


class CaptchaSolver:
    def __init__(self, DRIVER: BaseDriver):
        self.DRIVER = DRIVER

    @staticmethod
    def url_to_id(captcha_url):
        return captcha_url.split("/")[-1].split(".")[0]

    @staticmethod
    def id_to_url(captcha_id):
        return f"https://refor.detran.rj.gov.br/ReforWeb/uicrefor/696d6167656d/{captcha_id}.jpg"

    def valid_url(self, captcha_url):
        captcha_id = self.url_to_id(captcha_url)
        if self.id_to_url(captcha_id) == captcha_url:
            raise ValueError("Invalid captcha url")
        return captcha_id

    def get_image_id(self):
        image_element = self.DRIVER.find_locator("captchaImage")
        image_url = image_element.get_attribute("src")
        image_id = self.url_to_id(image_url)

        return image_id

    @staticmethod
    def valid_id(captcha_id):
        if not (captcha_id in CAPTCHA_ANSWERS and len(CAPTCHA_ANSWERS[captcha_id]) > 0):
            raise ValueError("Invalid captcha id")

    def get_answer(self, captcha_url):
        captcha_id = self.valid_url(captcha_url)
        self.valid_id(captcha_id)
        return CAPTCHA_ANSWERS[captcha_id]

    def submit_answer(self, captcha_answer):
        input_element = self.DRIVER.find_locator("captchaInput")
        input_element.clear()
        input_element.send_keys(captcha_answer)

        self.DRIVER.find_locator("captchaSendButton", method='click')

    def verify_result(self, infos) -> int:
        """
        :return: 0 if captcha is solved,
                    1 if captcha answer was empty,
                    2 if the category has no stalls available,
                    3 if the captcha answer was not valid,
                    4 if category has no available veicles
                    5 if schedule is not available
        """
        error_xpath = "//td[@data-testtoolid='statusbar_textocurto']/span/a/font/b"
        error_texts = [
            "Digite o Texto da Imagem.",
            "N??O EXISTEM BANCAS DISPON??VEIS",
            "Texto informado n??o corresponde ao texto da imagem.",
            "N??O EXISTE VE??CULO PARA ESTA CATEGORIA",
            "AGENDAMENTO AINDA N??O LIBERADO. A LIBERA????O EST?? PREVISTA PARA"
        ]


        try:
            error_element = self.DRIVER.find_element(error_xpath, retry_count=1)
            if infos is not None:
                self.DRIVER.returnMsg(self, infos, error_element.text.strip())

            for error in error_texts:
                if error in error_element.text.strip():
                    return error_texts.index(error) + 1
        except NoSuchElementException:
            pass
        return 0

    def solve(self, infos=None):
        ready = False
        retries = 0
        while not ready:
            image_id = self.get_image_id()
            try:
                captcha_answer = self.get_answer(image_id)
            except ValueError:
                self.DRIVER.find_locator("captchaReloadButton", method='click')
                time.sleep(0.5)
                retries += 1
                continue

            self.submit_answer(captcha_answer)
            submit_result = self.verify_result(infos)

            if submit_result == 0:
                ready = True
            elif submit_result == 2:
                raise Exception("No stalls available")
            elif submit_result == 3:
                self.DRIVER.find_locator("captchaReloadButton", method='click')
                retries += 1
            elif submit_result == 4:
                raise Exception("No available vehicles")
            elif submit_result == 5:
                raise Exception("Schedule not available")
            else:
                raise Exception("Unknown captcha result")

