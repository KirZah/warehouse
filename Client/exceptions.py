# Стоит добавить try except, чтобы db.py был более независимым от client.py
from loguru import logger as lg


class DBError(Exception):
    msg = "Error!"

    def __init__(self, message="Unknown database error!"):

        lg.debug("Unknown database error!")

        if message is None:
            self.message = "(Default) Database error!"
        else:
            self.message = message
        super().__init__(self.message)


class DBConnectionError(DBError):
    msg = "Connection Error!"

    def __init__(self, message=None):
        lg.debug(f"Could not reconnect!")
        if message is None:
            self.message = "(Default) Connection error!"
        else:
            self.message = message
        super().__init__(self.message)


