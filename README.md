# AM4 bot

## Installation
```
apt-get -y install build-essential libmysqlclient-dev libboost-all-dev python3.10 python3.10-pip python3.10-wheel python3.10-dev python3.10-venv software-properties-common unixodbc unixodbc-dev
pipenv --clear install
python3 -c "import pyarrow; pyarrow.create_library_symlinks()"
CFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" pip3 install --no-cache-dir turbodbc
python3 -c "import turbodbc.cursor as c; print(c._has_arrow_support(), c._has_numpy_support())"
```