import sys
import pandas as pd
import yaml
import getpass
import re
from datetime import datetime
from netmiko import ConnectHandler

def loadcsvdict(filenam, indexcolnam):
    # Load the csv file and output list of dictionary

    devlistdf = pd.read_csv(filenam, index_col=indexcolnam)
    print(filenam)
    # return devlistdf.to_records() # convert to list of tuples
    # return devlistdf.to_dict()  # convert to dictionary of headings
    return devlistdf  # return as pandas data frame

def writedftocsv(pandadf, filenam):
    # Write pandas data frame to csv file

    pandadf.to_csv(filenam)
    return True

def loadconfyml(filenam):
    """ 
    Load the conifuration file written in YAML format
    into python 
    """

    with open(filenam, "r") as file_descriptor:
        cfgdata = yaml.load(file_descriptor)
    # file_descriptor.close()
        #print(list(cfgdata))
    #for i in cfgdata:
    #    print(i)
        return cfgdata

def connruncmd(cmdlist, **devicecon):
    """ Connect to the device and run the list of commands

    - **devcecon is dictionary of below format 
    r2 = {
    'device_type': 'cisco_ios_telnet', # device_type = 'cisco_ios' for SSH
    'ip':   '192.168.239.135',
    'username': 'test',
    'password': 'password',
    'port' : 5004,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
        }

    - *cmdlist is the list of commands to run
    """

    print("func start")
    print(devicecon)
    print("func end")
    print(cmdlist)
    cmdout = []

    try:
        netconn = ConnectHandler(**devicecon)

        for runcmd in cmdlist:
            cmdout = netconn.send_command(runcmd)
            print(cmdout)
    
        netconn.disconnect()
    
    except (ValueError, IOError) as err:
        cmdout = err


    print(cmdout)
    return cmdout

def cmdrun(devname, kdev, kcmd):
    """ Connect to the device and run the list of commands

    - **devcecon is dictionary of below format 
    r2 = {
    'device_type': 'cisco_ios_telnet', # device_type = 'cisco_ios' for SSH
    'ip':   '192.168.239.135',
    'username': 'test',
    'password': 'password',
    'port' : 5004,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
        }

    - *cmdlist is the list of commands to run
    """

    print("cmdrun\n\n")
    print(kdev)

    cmdout = {}

    try:
        netconn = ConnectHandler(**kdev)
        # print(kdev)

        for cmditem in kcmd:
            # print(cmditem)
            # print(kcmd[cmditem]['clicmd'])
            # print(kcmd[cmditem]['regexmatch'])

            netcmdout = netconn.send_command(kcmd[cmditem]['clicmd'])
            # netcmdout = "bandwidth 10000"
            print(netcmdout)

            #outone = re.search(r"^bandwidth ([0-9]+)", "bandwidth 4000")
            outone = re.search(kcmd[cmditem]['regexmatch'], netcmdout)
            try:
                print(outone.group(1))
                cmdout[cmditem]=outone.group(1)
            except (IndexError, AttributeError) as err:
                errorout = "ERROR: "+str(err)
                print(errorout)
                cmdout[cmditem]=errorout

        netconn.disconnect()
    
    except Exception as err:
        cmdout['connstatus'] = 'Failed'
        cmdout['notes'] = err
    
    else:
        cmdout['connstatus'] = 'Success'
        cmdout['notes'] = 'None'

    print(cmdout)
 
    for wrcmdout in cmdout:
        print(cmdout[wrcmdout])
        print(wrcmdout)

        csvfileload.loc[devname, wrcmdout] = cmdout[wrcmdout]
    
    return cmdout


def main():
    # totalcmdops = len(sys.argv)
    # cmdops = sys.argv

    start_time = datetime.now()


    # get username credentials
    netuser = input('Enter username: ')
    netpass = getpass.getpass(prompt='Enter password: ')
    netenablepass = getpass.getpass(prompt='Enter enable password: ')


    global csvfileload 
    csvfileload = loadcsvdict(sys.argv[1], 'hostname')
    # print(totalcmdops, cmdops)
    # print(type(csvfileload))
    # print(csvfileload)

    # get unique devices from the dataframe 
    devoncsv = csvfileload['devtype'].unique()
    # print(devoncsv)


    # Load YAML configuration definitions
    cfgyamlfileload = loadconfyml(sys.argv[2])
    # print(cfgyamlfileload)

    # Extract Headings to be in CSV output file and add to the dataframe
    csvoutheadings = cfgyamlfileload['outputcsv']['headings']
    # print(csvoutheadings)
    for outheads in csvoutheadings:
        csvfileload[outheads] = 'NaN'
    
    # print(csvfileload)

    for dev in devoncsv:
        print("\n"+dev+"\n")
        if cfgyamlfileload[dev]:
            for field in cfgyamlfileload[dev]:
                print("\t"+field)
                cmd = cfgyamlfileload[dev][field]['clicmd']
                regex = cfgyamlfileload[dev][field]['regexmatch']
                print("\t\t"+cmd+"\n\t\t"+regex)
                #for i in devfieldlist:
                #    print(i, devfieldlist[i])
            # switchcmdlist = cfgyamlfileload[dev]
            # print(switchcmdlist)
        else:
            print('no load')

    # Iterate each record on the CSV Device list
    csvdict = csvfileload.to_dict('index')
    #print(csvdict)
    for devitem in csvdict:
        # print(csvdict[devitem])
        devtoconn = {
            'device_type': 'cisco_ios' if csvdict[devitem]['conntype'] == 'ssh' else 'cisco_ios_telnet',
            'ip': csvdict[devitem]['ipaddress'],
            'port': csvdict[devitem]['connport'],   # optional, defaults to 22
            'username': netuser,
            'password': netpass,
            'secret': netenablepass,     # optional, defaults to ''
            'verbose': False,       # optional, defaults to False
        }
        #print(csvfileload[devitem])

         
        # print(devtoconn)
        cmddict = cfgyamlfileload[csvdict[devitem]['devtype']]
        #print(cmddict)
        #print("\n")

        netconncmdout = cmdrun(devitem, devtoconn, cmddict)
        print(netconncmdout)

    #print("data frame bandwidth")
    # print(csvfileload['wan bandwidth'])

    """
    r2 = {
    'device_type': 'cisco_ios_telnet',
    'ip':   '192.168.239.135',
    'username': netuser,
    'password': netpass,
    'port' : 5006,          # optional, defaults to 22
    'secret': netenablepass,     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
    }

    """
    # r2cmd = ['show ver', 'show int desc']

    # connruncmd(r2cmd, **r2)

    writedftocsv(csvfileload, 'outcsv.csv')

    print("start time: " + str(start_time))
    endtime = datetime.now()
    print("end time: " + str(endtime))
    print ("\nElapsed time to  run commands: {}s".format(str(datetime.now() - start_time)))


if __name__ == '__main__':
    main()
