# ecourse

## Installation
### Python module
* pip install -r requirement.txt

### Node.js (LTS Version: v6.x)
windows:
* https://nodejs.org/en/

linux: 
* curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
* sudo apt-get install -y nodejs

### MySQL
MySQL Installer [link](http://dev.mysql.com/downloads/installer/)
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
cd ecourse_web
npm install
webpack
```

### Testing
```
pytest --junitxml=test_report.xml --cov=. --cov-report xml --cov-report html
```
report: htmlcov index.html
