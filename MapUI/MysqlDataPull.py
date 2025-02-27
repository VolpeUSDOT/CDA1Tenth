import pandas as pd

# import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import datetime as dt
import warnings
import json
from sqlalchemy import text
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


class Database:
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
        # self.dbconn = self._FindDatabaseConnection()
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
        warnings.simplefilter(action="ignore", category=UserWarning)
        actionsQuery = f"""SELECT * FROM `{self.schema}`.`action`;"""
        action_data = pd.read_sql(actionsQuery, con=self.engine)
        return action_data

    def createSQLEngine(self):
        with open("secrets.json") as f:
            secrets = json.load(f)

        # mysqlconnector
        engine = create_engine(
            f"mysql+pymysql://{secrets['user']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{self.schema}"
        )
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

    def updateActionNotify(self, action_id, area_is_notify):
        """
        Update the action data in the database
        """
        area_is_notify = 1 if area_is_notify else 0
        actionsQuery = (
            f"""SELECT * FROM `{self.schema}`.`action` where action_id = {action_id};"""
        )
        action = pd.read_sql(actionsQuery, con=self.engine)
        if not action.empty:
            action.at[0, "area_is_notify"] = area_is_notify
            update_query = text(
                f"UPDATE `{self.schema}`.`action` SET area_is_notify = :area_is_notify WHERE action_id = :action_id"
            )
            with Session(self.engine) as session:
                session.execute(
                    update_query,
                    {"area_is_notify": area_is_notify, "action_id": action_id},
                )
                session.commit()
            logging.info(
                "Action(id=%s) area_is_notify updated to %s", action_id, area_is_notify
            )
        else:
            logging.info("Action(id=%s) not found", action_id)
        return action

    def updateActionAreaName(self, action_id, area_name):
        """
        Update the area name of action data in the database
        """
        actionsQuery = (
            f"""SELECT * FROM `{self.schema}`.`action` where action_id = {action_id};"""
        )
        action = pd.read_sql(actionsQuery, con=self.engine)
        if not action.empty:
            action.at[0, "area_name"] = area_name
            update_query = text(
                f"UPDATE `{self.schema}`.`action` SET area_name = :area_name WHERE action_id = :action_id"
            )
            with Session(self.engine) as session:
                session.execute(
                    update_query,
                    {"area_name": area_name, "action_id": action_id},
                )
                session.commit()
            logging.info("Action(id=%s) area_name updated to %s", action_id, area_name)
        else:
            logging.info("Action(id=%s) not found", action_id)

    def updateNextActionId(self, action_id, next_action_id):
        """
        Update the next action id of action data in the database
        """
        actionsQuery = (
            f"""SELECT * FROM `{self.schema}`.`action` where action_id = {action_id};"""
        )
        action = pd.read_sql(actionsQuery, con=self.engine)
        if not action.empty:
            action.at[0, "next_action_id"] = next_action_id
            update_query = text(
                f"UPDATE `{self.schema}`.`action` SET next_action_id = :next_action_id WHERE action_id = :action_id"
            )
            with Session(self.engine) as session:
                session.execute(
                    update_query,
                    {"next_action_id": next_action_id, "action_id": action_id},
                )
                session.commit()

    def getLastActionId(self):
        """
        Get the last action id from the database
        """
        actionsQuery = f"""SELECT * FROM `{self.schema}`.`action` ORDER BY action_id DESC LIMIT 1;"""
        action = pd.read_sql(actionsQuery, con=self.engine)
        if not action.empty:
            return action.at[0, "action_id"]
        else:
            return -1

    def insertNewActionPoint(self, actionPoint):
        """
        Insert new action point into the database
        """
        last_action_id = self.getLastActionId()
        actionPoint.actionID = last_action_id + 1
        actionPoint.prev_action = last_action_id
        actionPoint.next_action = -1
        insert_query = text(
            f"INSERT INTO `{self.schema}`.`action` (action_id, prev_action_id, next_action_id, area_name, area_lat, area_long, area_is_notify, area_status) VALUES (:action_id, :prev_action_id, :next_action_id, :area_name, :area_latitude, :area_longitude, :area_is_notify, :area_status)"
        )
        with Session(self.engine) as session:
            session.execute(
                insert_query,
                {
                    "action_id": actionPoint.actionID,
                    "prev_action_id": actionPoint.prev_action,
                    "next_action_id": actionPoint.next_action,
                    "area_name": actionPoint.name,
                    "area_latitude": actionPoint.latitude,
                    "area_longitude": actionPoint.longitude,
                    "area_is_notify": actionPoint.is_notify,
                    "area_status": "OPEN" if actionPoint.status else "CLOSED",
                },
            )
            session.commit()
            logging.info("New action point inserted")

        # After insert new action, update the previous last action's next action id to the new action id
        self.updateNextActionId(last_action_id, actionPoint.actionID)
        return actionPoint.actionID


if __name__ == "__main__":
    print("test")
    ap_df = pd.DataFrame({"TestCol": [2, 3, 4, 5, 6, 7], "AP_ID": [1, 2, 3, 4, 5, 6]})

    SQLdb = Database("PORT_DRAYAGE")

    engine = SQLdb.createSQLEngine()

    ap_df.to_sql(
        "action",
        con=engine,
        if_exists="replace",
        index=False,
        schema="PORT_DRAYAGE",
    )
