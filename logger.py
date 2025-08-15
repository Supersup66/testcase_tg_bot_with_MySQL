import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
    filename='main.log', mode='w', encoding='utf-8')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(funcName)s %(lineno)d \n%(message)s\n'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
