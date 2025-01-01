# controllers/model_controller.py
import datetime
from models.tables.accounts import Accounts
from models.tables.users import Users

class ModelController:
    def __init__(self, db):
        self.db = db

