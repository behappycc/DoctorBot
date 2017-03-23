# DoctorBot

## Installation
### Python module
* sudo pip3 install -r requirement.txt
### apt-get module
* sudo chmod +x setup_environment.sh
* sudo ./setup_environment.sh

### Node.js (LTS Version: v6.x)
windows:
* https://nodejs.org/en/

linux: 
* curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
* sudo apt-get install -y nodejs
* sudo npm install webpack -g

### MySQL
windows:
MySQL Installer [link](http://dev.mysql.com/downloads/installer/)

linux:
* sudo apt-get update
* sudo apt-get install mysql-server
* sudo mysql_secure_installation
* sudo mysql_install_db
```
mysql> CREATE DATABASE db_doctorbot;
mysql> CREATE USER 'doctorbot'@'%' IDENTIFIED BY 'dbdev';
mysql> GRANT ALL PRIVILEGES ON db_doctorbot.* TO 'doctorbot'@'%' ;
mysql> FLUSH PRIVILEGES;
```

### Document Web APIs
* http://localhost:8000/docs/

###Usage
```
cd doctorbot
npm install
webpack
python3 manage.py check
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```

### Testing
```
pytest --junitxml=test_report.xml --cov=. --cov-report xml --cov-report html
```
report: htmlcov index.html
