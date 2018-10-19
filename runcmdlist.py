#!/usr/bin/env python3
# coding=utf-8

import sys
import pandas as pd
import yaml
import getpass
import re
import os
from datetime import datetime
from netmiko import ConnectHandler
from multiprocessing import Process, Queue
import infoscrapmodule as infomod
from pathlib import Path

def makedir(dirname):
    """ created the directory

    Syntax: makedir("directory name")
    Output: Successful or not as string with errorcode

    checks if the directory exists;
    if not then creates the direcotry

    It will create even it have multiple direcotries
    in the path
    
    """

    dirpath = Path(dirname)
    # print(dirpath)
    
    try:
        if not dirpath.is_dir():
            dirpath.mkdir(parents=True)
    except Exception as err:
        status = "Directory creation ERROR: " + err + "\n"
    else:
        status = "Directory creation successful\n"
    
    return status



def write_to_file(filename, mode, data):
    # Write to the file
    print(filename+mode)
    f = open(filename, mode)
    f.write(data)
    f.close()


def runcmdlist(devname, kdev, kcmd, koutdir, output_q):
    """ Connect to the device and run the list of commands

    - kdev = dictionary of the device for connection parameters
    **devcecon is dictionary of below format 
    r2 = {
    'device_type': 'cisco_ios_telnet', # device_type = 'cisco_ios' for SSH
    'ip':   '192.168.239.135',
    'username': 'test',
    'password': 'password',
    'port' : 5004,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
        }

    - kcmd = cmdlist is the list of commands to run
    """

    print("\n\n")
    print(devname + "--> RUNNING")
    # print(kdev)
    # print(kcmd)

    # Instantiate Path class for the OS file and directory access
    outpath = Path(koutdir)

    # DataFrame to track the each device command run
    cmdout = {}
    cmdoutdf = pd.DataFrame()


    timenow = datetime.today()
    timestr = timenow.strftime('_%Y%m%dT%H%M%S')
    # "Capture time: " + str(datetime.now()) + "\n"

    filename = os.path.join(outpath.resolve(), (devname + timestr +'.cfg'))
    # filename = outpath.joinpath(devname + timestr + '.cfg')
    # filename = str(outpath.resolve()) + '' + timestr + '.cfg'
    
    # print(filename, type(filename), timestr)

    fp = open(filename, 'w')
    # write_to_file(filename, 'a', timestr)
    # write_to_file(filename, 'a', '\n'.join(kcmd))

    fp.write("! " + devname + "\n\n") 
    fp.write("! Capture time: " + timestr + "\n\n")

    try:
        netconn = ConnectHandler(**kdev)
        netconn.enable()
        netconn.find_prompt()


        for icmd in kcmd:
            print(icmd)
            fp.write("\n!"+icmd+"\n\n")

            netcmdout = netconn.send_command(icmd)
            # print(netcmdout)
            fp.write(netcmdout)

        netconn.disconnect()

    except Exception as err:
        cmdout['connstatus'] = 'Failed'
        cmdout['notes'] = err
        fp.write("! Device connection: " + cmdout['connstatus'])
    
    else:
        cmdout['connstatus'] = 'Success'
        cmdout['notes'] = 'None'
        fp.write("! Device connection: " + cmdout['connstatus'])


    for wrcmdout in cmdout:
        # print(cmdout[wrcmdout])
        # print(wrcmdout)

        # csvfileload.loc[devname, wrcmdout] = cmdout[wrcmdout]
        cmdoutdf.loc[devname, wrcmdout] = cmdout[wrcmdout]

    fp.close()
    
    output_q.put(cmdoutdf)
    # return cmdout

def main():
    # csvfileload = pd.DataFrame()

    totalops = len(sys.argv)
    # print(totalops)
    # cmdops = sys.argv
    start_time = datetime.now()

    if totalops <= 3 or totalops > 4:
        infomod.syntaxdisp("mismatch in number of arguments given")
        return("No input file provided")

    else:
        # Load CSV Device list in to Pandas dataframe with Hostname as index 
        csvfileload = infomod.loadcsvdict(sys.argv[1], 'hostname')

        # Load YAML configuration definitions
        cfgyamlfileload = infomod.loadconfyml(sys.argv[2])
        ## print(cfgyamlfileload)


    # get username credentials
    netuser = input('Enter username: ')
    netpass = getpass.getpass(prompt='Enter password: ')
    netenablepass = getpass.getpass(prompt='Enter enable password: ')


    
    # print(totalcmdops, cmdops)
    # print(type(csvfileload))
    # print(csvfileload)

    # get unique devices from the dataframe 
    devoncsv = csvfileload['devtype'].unique()
    print(devoncsv)


    # Load YAML configuration definitions
    cfgyamlfileload = infomod.loadconfyml(sys.argv[2])
    print(cfgyamlfileload)

    for dev in devoncsv:
        # print(dev)
        print(cfgyamlfileload[dev])

    # Iterate each record on the CSV Device list
    csvdict = csvfileload.to_dict('index')
    #print(csvdict)
    
    #setup multiprocessing queue
    # output_q = Queue(maxsize=20)
    output_q = Queue()
    procs = []

    # output directory creation
    outdir = cfgyamlfileload['moduleconf']['outputdir']
    dirstatus = makedir(outdir)
    print(dirstatus)

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
        # print(cmddict)
        # print("\n")

        my_proc = Process(target=runcmdlist, args=(devitem, devtoconn, cmddict, outdir, output_q))
        my_proc.start()
        procs.append(my_proc)

        
        # netconncmdout = cmdrun(devitem, devtoconn, cmddict)
        # print(netconncmdout)

    #print("data frame bandwidth")
    # print(csvfileload['wan bandwidth'])

    csvfileload['connstatus']=''
    csvfileload['notes']=''
    # Make sure all processes have finished
    for a_proc in procs:
        a_proc.join()

    while not output_q.empty():
        my_df = output_q.get()
        print(my_df)
        csvfileload.update(my_df)
       
    try:
        outputfile = sys.argv[3]
        # print(outputfile)
    except IndexError:
        outputfile = 'outcsv.csv'
    else:
        print(csvfileload)
        infomod.writedftocsv(csvfileload, outputfile)
        print("\n\nOutput is written to director: %s \n" %(outdir))
    
    # print("start time: " + str(start_time))
    endtime = datetime.now()
    # print("end time: " + str(endtime))
    print ("\nElapsed time to  run commands: {}s".format(str(endtime - start_time)))


if __name__ == '__main__':
    main()
