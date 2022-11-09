import logging
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from seleniumide.init import *
from src.refor import Refor

class verify_pratical_exame(Refor):

    def search_links(self, category: str):
        self.find_locator("praticalExamSchedule", method="click")
        self.find_locator("verifyPraticalExame", method="click")
        self.switch_to_screen("VerifyPraticalExam")


    @BaseDriver.screen_decorator("VerifyPraticalExam")
    def set(self, category):
        pass

    def choose_schedule_grid_option(self, renach: str, category: str):
        self.set_protocolo_grid_option(renach)
        self.set_category_grid_option(category)
        self.find_locator("verifyButton", method="click")
        time.sleep(5)
        self.check_text_result()
        if self.loop is False: 
            return self.loop
        schedule_grid_dic = self.convert_schedule_grid_option_to_dict()
        self.set_option_pratical(schedule_grid_dic)

    def set_protocolo_grid_option(self, renach):
        input_element = self.find_locator("renachInput1")
        input_element.clear()
        input_element.send_keys(renach)
        

    def set_category_grid_option(self, category):
        select_element = self.find_locator("categorySelect")
        select_object = Select(select_element)
        select_object.select_by_value(category)

    def convert_schedule_grid_option_to_dict(self):
        info_dict = {}

        soap = BeautifulSoup(self.DRIVER.page_source, 'html.parser')
        select_element = soap.select('td.LABELCellNormal')[2:]

        for num, element in enumerate(select_element):
            script = f"return document.querySelectorAll('input.FIELDInputDisplay')[{num}].CASA_lastControlValue"
            info_dict.update({element.text: self.DRIVER.execute_script(script)})

        logging.info(info_dict)
        return info_dict


    def set_option_pratical(self, schedule_grid:dict):
        self.find_locator("cancelButton", method="click")
        msg = 'Cancelamento realizado com sucesso.'
        if msg in self.DRIVER.page_source:
            schedule_grid.update({'msg': msg, 'cancelado': True})

            if self.current_user == self.total_user:
                self.infos.update({"sucesso": "S", "cancelado": "S"})
                self.savePratic(self.infos)
                
                self.infos.update({"sucesso": "S", "cancelado": "S"})
                self.saveScheduled(self.infos)
            else: 
                self.infos.update({"sucesso": "S", "cancelado": "S"})
                self.saveScheduled(self.infos)

            logging.info(schedule_grid)
            self.loop = False
            return self.loop

    
    def check_text_result(self):
        responseText = self.DRIVER.execute_script('''return document.querySelector('[data-testtoolid="statusbar_textocurto"]').textContent''')

        texts = [
            "CANDIDATO NÃO AGENDADO",
            "CANCELAMENTO DE AGENDAMENTO DEPOIS DO PRAZO"
            ]

        try:
            for msg in texts:
                if msg in responseText.strip():
                    msg_error = f"Text error: {msg} found"
                    self.infos.update({'log': msg_error })
                    self.infos.update({"sucesso": "N", "cancelado": "N"})
                    self.savePratic(self.infos)
                    self.loop = False
                    return 
        except NoSuchElementException:
            pass
        return 0




    def get_schedule_pratical(self, protocolo: str, category: str):
        pass
