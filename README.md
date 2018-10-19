# infoscrapper

## Usage
    Syntax: infoscrapmodule.py <devicelist.csv> <scapcfgdefinitions.yaml> <output.csv>
        - devicelist.csv
            - device list csv with beblow headings
                -   `hostname,ipaddress,devtype,conntype,connport,sitename`
        - scapcfgdefinitions
            - YAML file with definistions of commands to be run relevant to any headings above
        - output.csv
            - name of the output file in csv format
## example
python infoscrapmodule.py devicelistgsn3.csv cfgdescswitch.yaml output.csv

# runcmdlist

## Usage
    Syntax: infoscrapmodule.py <devicelist.csv> <command_list_definitions.yaml> <output.csv>
        - devicelist.csv
            - device list csv with beblow headings
                -   `hostname,ipaddress,devtype,conntype,connport,sitename`
        - command_list_definitions
            - YAML file with definistions of list of commands to be run relevant to each device type
        - output.csv
            - name of the output file in csv format showing the status of each devices command run status
## example
python runcmdllsit.py devicelistgns3_v2.csv cmdlist.yaml cmdoutcsv.csv


python runcmdllsit.py devicelistgns3_v2.csv cmdlist.yaml cmdoutcsv.csv

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
    pip3 install pyyaml

### Django setup

#### django project init
django-admin startproject infoscrapper .

#### Django app with project

python manage.py startapp infoscrapperapp
