import logging
import sys
import json
from src.crawlers.verify_pratical_exam_category import verify_pratical_exame
from src.crawlers.set_pratical_exam import set_pratical_exam
from src.api.db_imports import update_pid, get_argumentos
from sys import argv

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")


def main(crawler:str, kwargs:dict):
    if crawler == 'set_pratical_exam':
        with set_pratical_exam() as bot: 
            bot.start(**kwargs) 
    else:
        with verify_pratical_exame() as bot: 
            bot.start(**kwargs)
    logging.info("Working running")

inputArgs = sys.argv[1:]
content = get_argumentos(id=str(inputArgs[0]))
content_json = json.loads(content['parametros'])

if 'agendamentos' in content_json:
    content_json = content_json['agendamentos']

main(crawler=content_json['crawler'], kwargs=content_json)
