import streamlit as st
import pandas as pd
import mysql.connector
import os
import warnings


class Database():
    """
    Class to contain data and related functions for each webtool

    Style Guide:
    Use functions from this class instead of directly calling st.session_state 

    Attributes:
        None, the data is all stored globally in st.session_state

    """

    def __init__(self, schema):
        dbconn = self._FindDatabaseConnection()
        self.action_data = self._GetActionData(dbconn, schema)
    
    def getData(self):
        return self.action_data

    def _FindDatabaseConnection(self):
        """
        Connects to appropriate sql server based on environment
        """
        if "CMAQ_Tools_Environ" in os.environ:
            dbenviron = os.environ["CMAQ_Tools_Environ"]
        else:
            dbenviron = 'DEVELOP'

        if dbenviron == 'DEVELOP':
            dbconn = mysql.connector.connect(host=st.secrets["{}_db_credentials".format(dbenviron)].host, \
                                        port=st.secrets["{}_db_credentials".format(dbenviron)].port, \
                                        user=st.secrets["{}_db_credentials".format(dbenviron)].user, \
                                        password=st.secrets["{}_db_credentials".format(dbenviron)].password)

        if dbenviron == 'DEPLOY':
            dbconn = mysql.connector.connect(host=os.environ['MYSQLCONNSTR_host'], \
                                        port=os.environ['MYSQLCONNSTR_port'], \
                                        user=os.environ['MYSQLCONNSTR_user'], \
                                        password=os.environ['MYSQLCONNSTR_password'])
            
        return dbconn

    def _GetActionData(self, cnx, schema):
        warnings.simplefilter(action='ignore', category=UserWarning)
        actionsQuery = f'''SELECT * FROM `{schema}`.`freight`;'''
        action_data = pd.read_sql(actionsQuery, con=cnx)
        return action_data