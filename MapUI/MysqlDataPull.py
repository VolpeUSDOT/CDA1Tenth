import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import warnings
import json


class Database():
    """
    Class to contain data and related functions for each webtool

    Style Guide:
    Use functions from this class instead of directly calling st.session_state

    Attributes:
        None, the data is all stored globally in st.session_state

    """

    def __init__(self, schema):
        self.dbconn = self._FindDatabaseConnection()
        self.schema = schema
        self.action_data = self._GetActionData()

    def getData(self):
        return self.action_data

    def _FindDatabaseConnection(self):
        """
        Connects to appropriate sql server based on environment
        """
        with open("secrets.json") as f:
            secrets = json.load(f)

        dbconn = mysql.connector.connect(host=secrets["host"],
                                         port=secrets["port"],
                                         user=secrets["user"],
                                         password=secrets["password"])
        return dbconn

    def _GetActionData(self):
        warnings.simplefilter(action='ignore', category=UserWarning)
        actionsQuery = f'''SELECT * FROM `{self.schema}`.`freight`;'''
        action_data = pd.read_sql(actionsQuery, con=self.dbconn)
        return action_data

    def createSQLEngine(self):
        with open("secrets.json") as f:
            secrets = json.load(f)

        engine = create_engine(f"mysql+mysqlconnector://{secrets['user']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{self.schema}")
        return engine
