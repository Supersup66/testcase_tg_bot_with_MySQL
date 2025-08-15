from .connector import DatabaseConnector


connector = DatabaseConnector()


def fetch_users(message):
    connector.connect()
    query = "SELECT * FROM Tg_users WHERE telegram_id=%s"
    users = connector.execute_query(query, (message.chat.id,))
    connector.close()
    return users


def insert_user(message):
    telegram_id = message.contact.user_id
    phone_number = message.contact.phone_number
    first_name = message.contact.first_name or ''
    last_name = message.contact.last_name or ''
    username = message.from_user.username or ''
    new_user = (telegram_id, first_name, last_name, username, phone_number)
    connector.connect()
    query = """
        INSERT INTO Tg_users
        (telegram_id, first_name, last_name, username, phone_number)
        VALUES (%s, %s, %s, %s, %s);
        """
    connector.execute_query(query=query, params=new_user)
    connector.close()


class Order:

    def __init__(self, customer_id):
        self.connection = connector
        self.customer_id = customer_id
        self.order_quantity = 0
        self.order_date = ''
        self.order_options = ''

    def __str__(self):
        return (
            f'Заказ: {self.customer_id}, '
            f'{self.order_quantity}шт на {self.order_date}'
        )

    def save_to_db(self):
        try:
            insert_query = """
                INSERT INTO Orders (
                    customer_id,
                    quantity,
                    date,
                    options
                ) VALUES (%s, %s, %s, %s);
            """
            values = (
                self.customer_id,
                self.order_quantity,
                self.order_date,
                self.order_options
            )
            connector.connect()
            connector.execute_query(insert_query, values)
            connector.close()
        except Exception:
            return False
        return True
