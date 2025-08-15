import mysql.connector
from contextlib import closing
from mysql.connector import Error
import os
from dotenv import load_dotenv
from logger import logger

load_dotenv()


def create_connection():
    try:
        connection = mysql.connector.connect(
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            host=os.getenv('MYSQL_HOST'),
            port=os.getenv('MYSQL_PORT')
        )
        return connection
    except Error as err:
        logger.error(f"Ошибка при подключении к базе данных: {err}")
        raise


class DatabaseConnector:
    def __init__(self):
        self.connection = None

    def connect(self):
        if not self.connection or not self.connection.is_connected():
            try:
                self.connection = create_connection()
            except Error as err:
                logger.error(f"Ошибка при открытии соединения: {err}")
                raise
            else:
                db_Info = self.connection.server_info
                logger.debug(f"Connected to MySQL Server version: {db_Info}")

    def close(self):
        if self.connection and self.connection.is_connected():
            try:
                self.connection.close()
            except Error as err:
                logger.error(f"Ошибка при закрытии соединения: {err}")
                raise
            else:
                logger.debug("Connection to MySQL Server closed")

    def execute_query(self, query, params=None):
        try:
            with closing(self.connection.cursor(dictionary=True)) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                self.connection.commit()
                logger.debug(f'Запрос {query[:15]} успешно выполнен. {result}')
            return result
        except Error as err:
            logger.error(f"Ошибка при выполнении запроса: {err}")
            raise
