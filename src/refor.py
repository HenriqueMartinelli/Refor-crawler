import logging
import sqlite3
import json 
import requests
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from seleniumide.init import *
from src.api.db_imports import get_banco
logging.basicConfig(level=logging.INFO)


class Refor(BaseDriver):
    
    def __exit__(self, type, value, traceback):
        if self.DRIVER:
            self.DRIVER.quit()  
        logging.info('Work finished')
        
        
    def __enter__(self, ): 
        self.current_screen = None
        self.current_frame = None
        self.current_user = 0
        self.DRIVER = False
        return self


    def login(self, username: str, category:str, password: str, attemps=30, cont=0):
        while attemps:
            self.DRIVER.get(self.URL_BASE)
            self.switch_to_screen("Login")

            cont += 1
            self.DRIVER.delete_all_cookies()
            page = self.DRIVER.page_source
            try:
                if "host failed" in page:
                    raise Exception('Natural Disconnect')
                self.find_locator("usernameInput").send_keys(username)
                self.find_locator("passwordInput").send_keys(password)
                self.find_locator("enterButton", method='click')

                self.switch_to_screen("Home")
                self.find_locator("praticalExamSchedule")
                logging.info('Login Ok')
                return self.search_links(category)
            except (Exception, WebDriverException, TimeoutException) as e: 
                logging.warning(f'Failed to login, attempt: {cont}')
                attemps -= 1



    def start(obj, **kwargs):
        obj.set_variables(**kwargs)
        obj.total_user = len(obj.logins)
        obj.vacancies = len(obj.logins)
        
        for logon in obj.logins:
            obj.infos = logon
            obj.initSelenium(user=logon['usuario'], password=logon['senha'], category=logon['categoria'])

            obj.loop = True
            while obj.loop:
                if obj.current_attemps is not -1:
                    if obj.infos['attemps'] < 0: break
                try:
                    obj.set(category=logon['categoria'])
                    if "set_pratical_exam" in str(obj.current_work):
                        obj.choose_schedule_grid_option(logon['dates'], logon['times'],
                                                        logon['locations'], logon['veiculo'], logon['renach'], obj.vacancies)
                    else:
                        obj.choose_schedule_grid_option(logon['renach'], logon['categoria'])
                        
                except Exception as e:
                    if obj.loop == False: continue
                    logging.error(f"Fatal error: {e}")
                    obj.initSelenium(user=logon['usuario'], password=logon['senha'], category=logon['categoria'])


    def initSelenium(self, user:str, password:str, category:str, attemps=3):
        ready = False
        while not ready:
            if attemps == 0: break
            try:
                if self.DRIVER:
                    self.logout()
                    self.DRIVER.quit()
                    logging.info('Starting new bot')
            except Exception as e:
                logging.error(f"Error on logout: {e}")
                continue

            try:
                self.setDriver(executable_path=self.driver_path, chrome_options=self.chrome_options)
                self.login(username=user, password=password, category=category)
                self.DRIVER.implicitly_wait(1.5)
                ready = True
            except Exception as e:
                attemps -= 1
                logging.error(f"Error on restart bot, retrying: {e}")




    def set_variables(obj, **args):
        obj.logins = list()
        obj.scheduledOptions = dict()
        obj.current_work = args.get('crawler')

        try:obj.users = json.loads(args.get('usuarios'))
        except:obj.users = args.get('usuarios')

        for pos, login in enumerate(obj.users):
            user = dict()
            
            obj.current_attemps = args.get('tentativas', -1)
            user['id'] = args.get('id')
            user['attemps'] = int(args.get('tentativas', ''))
            user['caer'] = args.get('caer', '')
            user['usuario'] = login
            user['veiculo'] = args.get('veiculo', '')
            user['categoria'] = args.get('categoria', '')
            user['sucesso'] = args.get('sucesso', 'N')
            user['dates'] = args.get('datas', '')
            user['times'] =  args.get('horarios', '')
            user['locations'] = args.get('locais', '')
            print(user['locations'])
            user['webhook'] = args.get('webhook', '')

            try:user['senha'] = json.loads(args.get('senhas'))[pos]
            except:user['senha'] = args.get('senhas')[pos]
            try:user['renach'] = json.loads(args.get('protocolos'))[pos]
            except:user['renach'] = args.get('protocolos')[pos]
            obj.logins.append(user)


    @staticmethod
    def returnMsg(self, infos, msg):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if infos.get("sucesso") == True: sucesso = True
        else: sucesso = False

        finally_msg = {"timestamp": dt_string,
                       "log_webhook": {"sucesso": sucesso, "id": infos.get("id"), "tentativas": infos.get("attemps"), 
                       "Caer": infos.get('caer'), "login": infos.get("usuario"), "log": msg}}
        infos.update({'log': finally_msg})


    @staticmethod
    def saveDeleteSchedule(obj, data):
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()
        data['attemps'] = data['attemps'] - 1
        id = data.get('id')

        sql = f'''UPDATE detranrj_refor_praticos_agendados 
                    SET sucesso = '{data.get('sucesso', 'N')}', 
                    cancelado = '{data.get('cancelado', 'N')}'
                    WHERE detranrj_refor_praticos_id = {id} WHERE protocolo = '{data.get('protocolo')}';
                    '''

        print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

        obj.set_webhook(obj, url=data.get('webhook'), id=id, infos=data)
        return logging.info('Data entered successfully')


    @staticmethod
    def saveScheduled(obj, data):
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()

        sql = f'''INSERT INTO detranrj_refor_praticos_agendados (detranrj_refor_praticos_id, data, hora, local, protocolo, 
                    tentativas, sucesso, cancelado) 
                    VALUES ('{obj.id}', '{data.get('date')}', '{data.get('time')}',  '{data.get('location')}',
                    '{data.get('protocolo')}', '{data.get('attemps')}', '{data.get('sucesso')}', 
                    '{data.get('cancelado')}');'''


        cursor.execute(sql)
        id = cursor.lastrowid
        conn.commit()
        conn.close()
        logging.info('Data entered successfully')
        obj.set_webhook(obj, url=data.get('webhook'), id=id, infos=data)
        return logging.info(f'''successfully scheduled, id: {id}, renach: {data.get('renach')}, date: {data.get('date')}, 
                         time: {data.get('time')}, local: {data.get('location')}, sucesso: {'True'}''')


    @staticmethod
    def savePratic(obj, data):
        conn = sqlite3.connect('detran-services.s3db')
        cursor = conn.cursor()
        data['attemps'] = data['attemps'] - 1
        id = data.get('id')

        sql = f'''UPDATE detranrj_refor_praticos 
                    SET tentativas = '{ data['attemps']}', sucesso = '{data.get('sucesso', 'N')}', 
                    cancelado = '{data.get('cancelado', 'N')}', log = '{json.dumps(data.get('log', ''))}'
                    WHERE id = {id};'''

        print(sql)
        cursor.execute(sql)
        conn.commit()
        conn.close()

        try: obj.set_webhook(obj, url=data.get('webhook'), id=id, infos=data)
        except: obj.DRIVER.set_webhook(obj, url=data.get('webhook'), id=id, infos=data)
        return logging.info('Data entered successfully')


    @staticmethod
    def set_webhook(obj, url:str, id:str, infos:dict):
        try:
            result_json = infos['log']["log_webhook"]
            return requests.request('POST', url, json={'agendamento': result_json}, params={'id': id}, timeout=5)
        except Exception as e:
            logging.warning(f'Webhook Error: {e}')


    def logout(self):
        try:
            return self.find_locator("btnLogout",retry_count=10, retry_sleep=1, method='click')
        except:
            self.returnMsg(self, self.infos, "Não achou o botão de deslogar")
            
