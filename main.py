import logging
import multiprocessing 
import os
from src.crawlers.verify_pratical_exam_category import verify_pratical_exame
from src.crawlers.set_pratical_exam import set_pratical_exam
from src.api.db_imports import update_pid

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")


def thread_function(name, crawler, kwargs):
 
        logging.info("Thread %s: starting", name)

        with crawler() as bot: 
            bot.start(**kwargs) 
        logging.info("Thread %s: finishing", name)


def main(crawler:object, kwargs:dict):
    logging.info("Main    : before creating thread")
    kwargs.update({'crawler': str(crawler)})
    x = multiprocessing.Process(target=thread_function, args=(1, crawler, kwargs))
    logging.info("Main    : before running thread")
    x.start()
    pid= os.getpid()

    return update_pid(pid=pid, id=kwargs['id'])

