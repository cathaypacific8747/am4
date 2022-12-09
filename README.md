# AM4 bot

## Installation
```
apt-get -y install build-essential software-properties-common libmysqlclient-dev libboost-all-dev unixodbc unixodbc-dev
apt-get -y python3.10 python3.10-pip python3.10-wheel python3.10-dev python3.10-venv
pipenv --clear install
python3 -c "import pyarrow; pyarrow.create_library_symlinks()"
CFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" pip3 install --no-cache-dir turbodbc
python3 -c "import turbodbc.cursor as c; print(c._has_arrow_support(), c._has_numpy_support())"

wget https://dev.mysql.com/get/mysql-apt-config_0.8.24-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.24-1_all.deb
sudo apt-get update
sudo apt-get install mysql-server=8.0.31-1ubuntu20.04

sudo apt-get install mysql-community-client-plugins
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc_8.0.31-1ubuntu22.04_amd64.deb
sudo dpkg -i mysql-connector-odbc_8.0.31-1ubuntu22.04_amd64.deb

odbcinst -j
```

import attr
from typing import NamedTuple

TODO: use postgres/sqlite

<!-- wget https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.31-linux-glibc2.27-x86-64bit.tar.gz
tar -xvf mysql-connector-odbc-8.0.31-linux-glibc2.27-x86-64bit.tar.gz
cd mysql-connector-odbc-8.0.31-linux-glibc2.27-x86-64bit
sudo cp bin/* /usr/local/bin
sudo cp -r lib/* /usr/local/lib
sudo myodbc-installer -a -d -n "MySQL ODBC 8.0 Driver" -t "Driver=/usr/local/lib/libmyodbc8w.so"
sudo myodbc-installer -a -d -n "MySQL ODBC 8.0" -t "Driver=/usr/local/lib/libmyodbc8a.so" -->