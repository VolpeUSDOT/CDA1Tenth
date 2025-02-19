# Download MariaDB
https://mariadb.org/download/?t=mariadb&p=mariadb&r=11.4.5&os=windows&cpu=x86_64&pkg=msi&mirror=osuosl
Version 11.4.5
MSI Package

# During Install
Take note of port in installation
Set desired password 

# Open MySQL client (MariaDB)

CREATE DATABASE port_drayage;

Exit;

mysql -u root -p port_drayage < path/to/your/port_drayage_lane2 1.sql

# This should successfully create the port_drayage sql database from the .sql file

# Secrets.json should be placed in main directory

{
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "12345"
}

# Secrets.json notes
leave host as is
port is selected when installing MariaDB - match secrets.json with install setting if unsure of port type "@Hostname;" in mysql
Choose MySQL password chosen during install