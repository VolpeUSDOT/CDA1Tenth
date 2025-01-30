from PySide6.QtSql import QSqlDatabase, QSqlDriver
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QStackedWidget
from MapWidget.mapwidget import MapWidget, ActionPoint
from actioninfobox import ActionInfoBoxWidget
from aporderbox import APOrderBoxWidget
from tabBar import TabBar
from MysqlDataPull import Database
import pandas as pd
from sqlalchemy import text
import json


con = QSqlDatabase.addDatabase(QSqlDriver)
con.setDatabaseName("port_drayage.freight")

with open("secrets.json") as f:
    secrets = json.load(f)
con.setHostName(secrets["host"])
con.setPort(secrets["port"])
con.setUserName(secrets["user"])
con.setPassword(secrets["password"])

check = con.open()
print(check)



# if __name__ == "__main__":
#     print('test')
#     ap_df = pd.DataFrame({'TestCol': [2,3,4,5,6,7],
#                           'AP_ID': [1,2,3,4,5,6]})
#     print("=" *80)
#     engine = SQLConnection()
#     connection = engine.open()


#     print("=" *80)
#     print("=" *80)

#     # with engine.connect() as connection:
#     # connection.execute(text('drop table if exists port_drayage.freight'))
#     print('Insert Attempt')
#     ap_df.to_sql('freight', con=engine, if_exists='replace', index=False, schema='port_drayage',)
#         # connection.commit()
#         # connection.close()
#     print('Insert Finished')
