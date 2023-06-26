from selenium.webdriver.support.select import Select
import json
from seleniumide.init import *
from src.refor import Refor
from utils.captcha import solver
from utils.captcha.solver import CaptchaSolver


class set_pratical_exam(Refor):

    def get_pratical_exam_categories(self):
        select_element = self.find_locator("categorySelect")

        select_object = Select(select_element)
        categories = [option.get_attribute('value') for option in select_object.options]
        return categories

    def set_pratical_exam_category(self, category: str):
        categories = self.get_pratical_exam_categories()
        if category and category not in categories:
            raise ValueError(f"Category {category} not found")
        select_element = self.find_locator("categorySelect")    
        select_object = Select(select_element)
        select_object.select_by_value(category)


    def convert_schedule_grid_option_to_dict(self, grid_option: str) -> dict:
        info_dict = {}

        infos_and_others = grid_option.split(" - VAGAS - ")
        infos = infos_and_others[0].split(" - ")
        infos = [info.strip() for info in infos]
        others = infos_and_others[1]

        if others.startswith("RJ - "):
            others = others.replace("RJ - ", "")
        if "QT-PRIM" in others:
            splited_others = others.rsplit(" ", 7)
            location = splited_others[0].strip()
            qt_prim = splited_others[3].strip()
            qt_repr = splited_others[7].strip()
        else:
            splited_others = others.split("-")
            location = splited_others[0].strip()
            qt_prim = None
            qt_repr = None

        info_dict["date"] = infos[0]
        info_dict["time"] = infos[1]
        info_dict["vagas"] = infos[2]
        info_dict["location"] = location
        info_dict["qt_prim"] = qt_prim
        info_dict["qt_repr"] = qt_repr
        info_dict["others"] = others
        return info_dict

    @BaseDriver.screen_decorator("PraticalExamScheduleRequestForm")
    def get_schedule_grid_options(self):
        self.find_locator("dateOptionSelect", method="visible")
        select_element = self.find_locator("dateOptionSelect")
        select_object = Select(select_element)
        options_str = [option.text for option in select_object.options]
        options = [self.convert_schedule_grid_option_to_dict(option) for option in options_str]
        return options


    def ready_schedule(self, options:list[any], vehicle:str, renach:str, infos:dict):
        print(self.scheduledOptions, vehicle, renach, infos)
        return self.set_item_options([self.scheduledOptions], options, vehicle, renach, infos)

    def set_item_options(self, setsOptions, options:list[any], vehicle:str, renach:str, infos:dict):
        for item in setsOptions:
            try:
                self.set_schedule_grid_option(options.index(item))
            except Exception as error:
                msg =  'OPÇÃO SELECIONADA, NÃO ESTÁ MAIS NA LISTA'
                self.returnMsg(self, self.infos, msg)
                self.savePratic(self, self.infos)
                
            self.set_pratical_exam_vehicle(vehicle)
            self.set_renach(renach)
            CaptchaSolver(self).solve(self.infos)

            try:
                verify_schedule = self.DRIVER.execute_script('''return document.querySelector('[data-testtoolid="w_renach1_msg"]').value''')
                if "JÁ AGENDADO" in verify_schedule:
                    self.returnMsg(self, self.infos, "JA AGENDADO")
                    self.savePratic(self, self.infos)
                    self.loop = False
                    return False
            except:pass

            self.check_text_error()
            if infos.get('log', '') != '':
                self.savePratic(self, self.infos)
                return self.callBack()

            self.verifyResultSchedule(self.infos, item)
            if self.loop == False:
                return self

            else:
                infos.update({"cancelado": 'N',"sucesso": "N"})
                self.savePratic(self, self.infos)
        
        msg = (f"Sem Agendamentos Disponíveis Para As Datas: {json.dumps(self.infos['dates'])}, Horários: {json.dumps(self.infos['times'])}, "
                f"Locais de Prova: {json.dumps(self.infos['locations'])}")
        self.returnMsg(self, self.infos, msg)
        self.savePratic(self, self.infos)
        
        return self.callBack()


    def choose_schedule_grid_option(self, dates: list[str], times: list[str], locations: list[str],
                                         vehicle: str, renach: str, vacancies: int):
        self.find_locator("dateOptionSelect", method="visible")

        infos = dict()
        setsOptions = list()
        infos.update({'vehicle': vehicle, 'renach': renach, 'category': self.infos['categoria']})
        options = self.get_schedule_grid_options()

        if self.scheduledOptions != {}:
                self.ready_schedule(options, vehicle, renach, infos)

        else:
            for option in options:

                if dates and option["date"] not in dates:
 
                    if dates == ['']: pass
                    else:continue

                if [t for t in times if option['time'][:2] in t] == []:
                    if times == ['']: pass
                    else:continue

                if locations and option["location"] not in locations:
                    if locations == ['']: pass
                    else:continue

                if option["vagas"] is None:
                    option["vagas"] = int(vacancies) + 1

                if "LIVRE DE COTA" not in option["others"]:
                    if not int(option["vagas"]) > int(vacancies):
                        continue

                    if option["qt_prim"] is None:
                        option["qt_prim"] = 1

                    if int(option["qt_prim"]) <= 0:
                            continue

                setsOptions.append(option)
            
            self.set_item_options(setsOptions, options, vehicle, renach, infos)


    @BaseDriver.screen_decorator("PraticalExamScheduleRequestForm")
    def set_schedule_grid_option(self, option_index: int):
        select_element = self.find_locator("dateOptionSelect")
        select_object = Select(select_element)
        select_object.select_by_index(option_index)



    @BaseDriver.screen_decorator("PraticalExamScheduleRequestForm")
    def get_pratical_exam_vehicles(self):
        select_element = self.find_locator("vehicleOptionSelect")
        select_object = Select(select_element)
        vehicles = [option.get_attribute('value') for option in select_object.options]
        return vehicles

    @BaseDriver.screen_decorator("PraticalExamScheduleRequestForm")
    def set_pratical_exam_vehicle(self, vehicle: str):
        if vehicle and vehicle not in self.get_pratical_exam_vehicles():
            raise ValueError(f"Vehicle {vehicle} not found")

        select_element = self.find_locator("vehicleOptionSelect")
        select_object = Select(select_element)
        select_object.select_by_value(vehicle)

    @BaseDriver.screen_decorator("PraticalExamScheduleRequestForm")
    def set_renach(self, renach: str):
        input_element = self.find_locator("renachInput1")
        input_element.clear()
        input_element.send_keys(renach)


    @BaseDriver.screen_decorator("Home")
    def search_links(self, category):
        self.find_locator("praticalExamSchedule", method='click')
        self.find_locator("praticalExamScheduleRequest", method='click')
        self.switch_to_screen("PraticalExamScheduleRequest")


    @BaseDriver.screen_decorator("PraticalExamScheduleRequest")
    def set(self, category):
        from datetime import datetime

        self.set_pratical_exam_category(category)
        now = datetime.now()
        CaptchaSolver(self).solve(self.infos)
        now = datetime.now()
        self.switch_to_screen("PraticalExamScheduleRequestForm")

    def callBack(self):
        self.find_locator("btnVoltar", method='click')
        self.switch_to_screen("PraticalExamScheduleRequest")
    
    def verifyResultSchedule(self, infos:dict, options:dict):
        submit_result = self.check_text_result()

        if submit_result == 1:
            result_script = self.DRIVER.execute_script('''return document.querySelector('[data-testtoolid="w_agendamento_ok1"]').value''')

            self.returnMsg(self, infos, result_script)
            infos.update(options)
            self.scheduledOptions = options

            if self.current_user == self.total_user:
                infos.update({"sucesso": "S", "cancelado": "N"})
                self.savePratic(self, infos)
                
                infos.update({"sucesso": "S", "cancelado": "N"})
                self.saveScheduled(infos)
                self.logout()
            else: 
                infos.update({"sucesso": "S", "cancelado": "N"})
                self.saveScheduled(infos)
                self.logout()

            self.loop = False
            return 

        elif submit_result == 2:
            msg = 'Não possui cota'
            self.returnMsg(self, self.infos, msg)
            self.savePratic(self, infos)


    def saveToScheluded(self, infos, script):
        infos.update({"log": script, "sucesso": "S", "cancelado": "N"})
        self.saveScheduled(infos)


    def check_text_result(self):
        responseText = self.DRIVER.execute_script('''return document.querySelector('[data-testtoolid="w_agendamento_ok1"]').value''')
        print(responseText.strip())

        texts = [
            "PEDIDO AGENDADO PARA",
            "Não possui cota",
            ]

        try:
            for msg in texts:
                if msg in responseText.strip():
                    return texts.index(msg) + 1 
        except NoSuchElementException:
            pass
        return 0


    def check_text_error(self):
        try:
            responseText = self.DRIVER.execute_script('''return document.querySelector("#STATUSBARSTATUSBAR > table > tbody > tr > td.STATUSBARCell").innerText''')
            if responseText.strip() != '':
                self.returnMsg(self, self.infos, responseText)
                self.savePratic(self, self.infos)
        except:
            pass



