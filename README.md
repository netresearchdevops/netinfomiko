# infoscrapper

# Setup


## virtual environment
### windows

mkvirtualenv venv_infoscrapper
venv_infoscrapper\Scripts>activate.bat

* Set Project Directory
	setprojectdir . --> this is within the directory
* Deactivate
	deactivate
* Workon
	workon venv_infoscrapper

### install required modules
* activate virtual environment

* Pip Install
	pip3 install django
    pip3 install pandas
    pip3 install netmiko

### Django setup

#### django project init
django-admin startproject infoscrapper .

#### Django app with project

python manage.py startapp infoscrapperapp