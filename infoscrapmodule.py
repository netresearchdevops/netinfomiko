import sys
import pandas as pd
import yaml

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


def main():
    # totalcmdops = len(sys.argv)
    # cmdops = sys.argv

    csvfileload = loadcsvdict(sys.argv[1], 'hostname')
    # print(totalcmdops, cmdops)
    # print(type(csvfileload))
    print(csvfileload)


    cfgyamlfileload = loadconfyml(sys.argv[2])
    print(cfgyamlfileload)
    for i in cfgyamlfileload:
        print(i)
        for j in cfgyamlfileload[i]:
            print(cfgyamlfileload[i][j])

    print(cfgyamlfileload['router']['bandwidth']['bandwidthcmd'])



    # writedftocsv(csvfileload, 'outcsv.csv')

    """
    # if loadcsv returns dictionary then run below

    for fields in csvfileload:
        print("*** %s ***" % fields)
        for data in csvfileload[fields]:
            print(data, csvfileload[fields][data])

    """

if __name__ == '__main__':
    main()
