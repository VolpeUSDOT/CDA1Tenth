import pandas as pd
# import mysql.connector
from sqlalchemy import create_engine, text
import datetime as dt
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
        self.schema = schema
        self.engine = self.createSQLEngine()
        #self.dbconn = self._FindDatabaseConnection()
        self.action_data = self._GetActionData()

    def getData(self):
        return self.action_data

    # def _FindDatabaseConnection(self):
    #     """
    #     Connects to appropriate sql server based on environment
    #     """
    #     with open("secrets.json") as f:
    #         secrets = json.load(f)

    #     dbconn = mysql.connector.connect(host=secrets["host"],
    #                                      port=secrets["port"],
    #                                      user=secrets["user"],
    #                                      password=secrets["password"])
    #     print(dbconn)
    #     return dbconn

    def _GetActionData(self):
        warnings.simplefilter(action='ignore', category=UserWarning)
        actionsQuery = f'''SELECT * FROM `{self.schema}`.`action`;'''
        action_data = pd.read_sql(actionsQuery, con=self.engine)
        return action_data

    def createSQLEngine(self):
        with open("secrets.json") as f:
            secrets = json.load(f)

        #mysqlconnector
        engine = create_engine(f"mysql+pymysql://{secrets['user']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{self.schema}")
        return engine

    def insertHoldingAction(self, engine, holding_action):
        with engine.connect() as conn:
            trans = conn.begin()
            try: 
                new_action_query = text(f"""
                    INSERT INTO `{self.schema}`.`action` ({', '.join(holding_action.keys())})
                    VALUES ({', '.join(f':{k}' for k in holding_action)})
                """)

                conn.execute(new_action_query, holding_action)

                # Update the previous next_action_id to point to the new action
                conn.execute(text(f"""
                    UPDATE `{self.schema}`.`action`
                    SET next_action_id = :new_action
                    WHERE action_id = :current_action
                """), {"new_action": holding_action["action_id"], "current_action": holding_action["prev_action_id"]})

                # Update the next action's prev_action_id
                conn.execute(text(f"""
                    UPDATE `{self.schema}`.`action`
                    SET prev_action_id = :new_action
                    WHERE action_id = :next_action_id
                """), {"new_action": holding_action["action_id"], "next_action_id": holding_action["next_action_id"]})

                trans.commit()
                return

            except Exception as e:
                trans.rollback()
                raise e



if __name__ == "__main__":
    print('test')
    ap_df = pd.DataFrame({'TestCol': [2,3,4,5,6,7],
                          'AP_ID': [1,2,3,4,5,6]})

    SQLdb = Database('PORT_DRAYAGE')

    engine = SQLdb.createSQLEngine()

    ap_df.to_sql('action', con=engine, if_exists='replace', index=False, schema='PORT_DRAYAGE',)
