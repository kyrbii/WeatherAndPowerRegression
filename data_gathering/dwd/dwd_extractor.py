import csv
from ftplib import FTP
from io import BytesIO
import os
import re
from zipfile import ZipFile, Path

# FTP server details and data directory paths
DWD_FTP_SERVER = 'opendata.dwd.de'
DWD_DATA_BASE_DIR = '/climate_environment/CDC/observations_germany/climate/hourly/'

# Regular expressions for file and station list patterns
DWD_HISTORY_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{1,2})_([0-9]{5})_([0-9]{8})_([0-9]{8})_hist\.zip)'
DWD_RECENT_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{1,2})_([0-9]{5})_akt\.zip)'
DWD_STATION_LIST_PATTERN = '^(\d{5})\s+(\d{8})\s+(\d{8})\s+(-?\d{1,4})\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(.*?)\s+([A-ZÄÖÜa-zäöü-]+)\s+$'

# Paths for storing historical and recent data
HISTORY_PATH = 'historical'
RECENT_PATH = 'recent'
RAW_DATA_PATH = '/raw/zip/'
TXT_DATA_PATH = '/raw/txt/'

# data type to data dir mapping (see dwd ftp server structure https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/)
DATA_DIRS = { 'TU': 'air_temperature',
              'N' : 'cloudiness',
              'RR': 'precipitation',
              'SD': 'sun',
              'VV': 'visibility',
              'FF': 'wind' }



def getRelevantHistoryFilename(filenames, station, dataType, startDate):
    """
    Get the relevant history filen probably containing the data for the provided criteria.

    Args:
    - filenames: List of filenames to search.
    - station: Station code.
    - dataType: Type of data.
    - startDate: Start date for filtering.

    Returns:
    - Relevant filename or an empty string if not found.
    """

    stationFile = ''
    # iterate through all given filenames
    for filename in filenames:
        match = re.match(DWD_HISTORY_FILENAME_PATTERN, filename)
        if match:
            # group(2) -> typ (TU), group(3) -> station, group(4) -> startdate, group(5) -> enddate
            # file is relevant, if enddate of file after startDate
            if (match.group(2) == dataType) and (match.group(3) == station) and (match.group(5) > startDate):
                stationFile = filename

    return stationFile



def getFilteredRecentFilename(filenames, filename, station, dataType):
    """
    Get the relevant history filen probably containing the data for the provided criteria.

    Args:
    - filenames: List of filenames to search.
    - station: Station code.
    - dataType: Type of data.
    - startDate: Start date for filtering.

    Returns:
    - Relevant filename or an empty string if not found.
    """

    match = re.match(DWD_RECENT_FILENAME_PATTERN, filename)
    if match:
        if (match.group(2) == dataType) and (match.group(3) == station):
            filenames.append(match.group(1))



def getRecentFilename(ftp, station, dataDir, dataType):#
    """
    Get the relevant history filen probably containing the data for the provided criteria.

    Args:
    - filenames: List of filenames to search.
    - station: Station code.
    - dataType: Type of data.
    - startDate: Start date for filtering.

    Returns:
    - Relevant filename or an empty string if not found.
    """
    
    ftp.cwd(DWD_DATA_BASE_DIR)
    ftp.cwd(dataDir)
    ftp.cwd(RECENT_PATH)
    # get all filenames
    filenames = []
    ftp.dir(lambda filename: getFilteredRecentFilename(filenames, filename, station, dataType))
    if len(filenames) > 0:
        return filenames[0]
    return ''



def getStationFiles(ftp, startDate, endDate, station, dataType):
    """
    Get recent and history filenames from server covering the given date range

    Args:
    - ftp: an already open ftp connection
    - startDate: Start date for data extraction.
    - endDate: End date for data extraction.
    - station: Station code.
    - dataType: Type of data.

    Returns:
    - list of station/datatype/timerange-realted files on dwd data server to retrieve
    """

    # go to the base dir for hourly observation data for germany
    ftp.cwd(DWD_DATA_BASE_DIR)
    # change to the according data directory
    ftp.cwd(DATA_DIRS[dataType])

    # first check historical data
    ftp.cwd(HISTORY_PATH)
    # get all filenames
    filenames = []
    ftp.dir(filenames.append)
    # get relevant ones
    historyFile = getRelevantHistoryFilename(filenames, station, dataType, startDate)
    stationFiles = []
    
    # maybe history is not enough or no history at all?
    if (len(historyFile) > 0): 
        match = re.match(DWD_HISTORY_FILENAME_PATTERN, historyFile)
        stationFiles.append(match.group(1))
        if match.group(5) < endDate: # ok, we eventually have to check recent data in addition?
            fileName = getRecentFilename(ftp, station, DATA_DIRS[dataType], dataType)
            if len(fileName) > 0:
                stationFiles.append(fileName)
    else: # or as the only source
        fileName = getRecentFilename(ftp, station, DATA_DIRS[dataType], dataType)
        if len(fileName) > 0:
            stationFiles.append(fileName)

    return stationFiles



def downloadZipFile(ftp, dataDir, stationFiles, targetFileBase):
    """
    retrieve all the provided files from the dwd weather server and store them (as zip files) locally

    Args:
    - ftp: an already open ftp connection
    - dataDir, directory on ftp server where the data to retrieve lives
    - stationFiles: List of files to retrieve
    - targetFileBase: Base directory for storing files.
    """

    # do it for all filenames
    for stationFile in stationFiles:
        ftp.cwd(DWD_DATA_BASE_DIR)
        ftp.cwd(dataDir)
        if stationFile[-7:] == 'akt.zip': # historical or recent?
            ftp.cwd(RECENT_PATH)
        else:
            ftp.cwd(HISTORY_PATH)
        try:
            # eventually make target directories (if needed)
            os.makedirs(targetFileBase + RAW_DATA_PATH) 
        except FileExistsError:
            pass # ignore file already exists error
        # no do a binary transfer
        with open(targetFileBase + RAW_DATA_PATH + stationFile, 'wb') as downloadFile:
            ftp.retrbinary(f"RETR {stationFile}", downloadFile.write)



def extractStationData(stationFiles, targetFileBase, station, startDate, endDate, mapFunction):
    """
    retrieve all the provided files from the dwd weather server and store them (as zip files) locally

    Args:
    - ftp: an already open ftp connection
    - dataDir, directory on ftp server where the data to retrieve lives
    - stationFiles: List of files to retrieve
    - targetFileBase: Base directory for storing files.
    Returns:
    - stationData:
    """
    stationData = []
    tailDateHour = '0000000000'
    for stationFile in stationFiles:
        with ZipFile(targetFileBase + RAW_DATA_PATH + stationFile) as zip_file:
            for zippedFile in zip_file.namelist():
                if zippedFile[0:8] == 'produkt_':
                    data_file = Path(zip_file, at=zippedFile)
                    with data_file.open() as dataFile:
                        reader = csv.reader(dataFile, delimiter=';')
                        first = True
                        for row in reader:
                            if not first:
                                rowStation, rowDate, rowHour, rowData = mapFunction(row, station, startDate, endDate)
                                if (rowStation != None):
                                    if (rowDate + rowHour) > tailDateHour:
                                        stationData.append((rowStation, rowDate, rowHour, rowData))
                                        tailDateHour = rowDate + rowHour
                            first = False
    return stationData



def writeStationData(stationData, targetFileBase, station, dataType, columnNames):
    """
    Write station data to a CSV file.

    Args:
    - stationData: List of tuples containing station data.
    - targetFileBase: Base directory for storing files.
    - station: Station code.
    - dataType: Type of data.
    - columnNames: List of column names.
    """

    # eventually make target directories (if needed)
    try:
        os.makedirs(targetFileBase + TXT_DATA_PATH + station)
    except FileExistsError:
        pass # ignore file already exists error

    # construct target file name
    filename = targetFileBase + TXT_DATA_PATH + station + '/' + station + '_' + dataType + '.csv'

    # delete possible existing target file
    try:
        os.remove(filename)
    except:
        pass # ignore file does not exist error

    # write data to csv file
    # the structure is station, data and hour as the first three columns, the provided columns afterwards
    with open(filename, 'w', encoding='cp1252') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        headNames = ['station', 'date', 'hour']
        headNames.extend(columnNames)
        csvWriter.writerow(headNames)
        for dataLine in stationData:
            dataCells = []
            dataCells.append(dataLine[0])
            dataCells.append(dataLine[1])
            dataCells.append(dataLine[2])
            if isinstance(dataLine[3],tuple):
                for dataValue in dataLine[3]:
                    dataCells.append(dataValue)
            else:
                dataCells.append(dataLine[3])
            csvWriter.writerow(dataCells)
                        


def extractZipFile(ftp, startDate, endDate, station, dataType, targetFileBase, mapFunction, columnNames):
    """
    Get relevant zip files from ftp server, extract them and write contained data file

    Args:
    - ftp: an already open ftp connection
    - startDate: Start date for data extraction.
    - endDate: End date for data extraction.
    - station: Station code.
    - dataType: Type of data.
    - targetFileBase: Base directory for storing files.
    - mapFunction: Function for mapping and processing data.
    - columnNames: List of column names.
    """

    stationFiles = getStationFiles(ftp, startDate, endDate, station, DATA_DIRS[dataType], dataType)
    if (len(stationFiles) > 0): # there are data files, get them all and process them
        downloadZipFile(ftp, DATA_DIRS[dataType], stationFiles, targetFileBase)
        stationData = extractStationData(stationFiles, targetFileBase, station, startDate, endDate, mapFunction)
        writeStationData(stationData, targetFileBase, station, dataType, columnNames)



def getStations(ftp, dataType, targetFileBase):
    """
    get the list of stations reporting data for the given dataType.

    Args:
    - ftp: an already open ftp connection
    - dataType: Type of data.
    - targetFileBase: Base directory for storing files.
    """
    
    listOfAllStations = [] # resulting list

    data = BytesIO() # buffer for binary io

    # first historical
    stationListFile = DWD_DATA_BASE_DIR +  DATA_DIRS[dataType] + '/' + HISTORY_PATH + '/' + dataType + '_Stundenwerte_Beschreibung_Stationen.txt'
    try:
        ftp.retrbinary(f'RETR {stationListFile}', data.write)
    except:   
        # no historical stations, so try if there is a current one
        stationListFile = DWD_DATA_BASE_DIR +  DATA_DIRS[dataType] + '/' + RECENT_PATH + '/' + dataType + '_Stundenwerte_Beschreibung_Stationen.txt'
        try:
            ftp.retrbinary(f'RETR {stationListFile}', data.write)
        except:
            data = None
    # if there are stations (historical or recent), write them to the target file base
    # with their data: station-id, date of first probe, date of last probe, altitude, logitude, lattitude, name and federal state
    if data:
        print(f"writing to {targetFileBase + TXT_DATA_PATH + dataType + '_stations.csv'}")
        with open(targetFileBase + TXT_DATA_PATH + dataType + '_stations.csv', 'w', encoding='cp1252') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',')
            csvWriter.writerow(['station','date_from','date_to','altitude','longitude','lattitude','name','state'])
            data_as_str = data.getvalue().decode('cp1252')
            data_as_array = data_as_str.split('\r\n')
            line_cnt = 0
            for data_line in data_as_array:
                if line_cnt > 2: # skip header of source txt file
                    if (len(data_line) > 0):
                        match = re.match(DWD_STATION_LIST_PATTERN, data_line)
                        listOfAllStations.append(match.group(1))
                        csvWriter.writerow([match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6), match.group(7), match.group(8)])
                line_cnt += 1
    return listOfAllStations



def startup(dataType, dataDir, mapFunction, columnNames):
    """
    connect to ftp dwd server, get list of all stations and iterate through stations to retreive
    all relevant data files

    Args:
    - dataType: Type of data.
    - dataDir: Data directory on the FTP server.
    - mapFunction: Function for mapping and processing data.
    - columnNames: List of column names.
    """

    startDate = '20220101'
    endDate = '20221231'

    # connect to dwd ftp server
    ftp = FTP(DWD_FTP_SERVER)
    ftp.login()

    # where to store the data locally
    targetFileBase = '.'

    # get all stations for the data type and iterate over them
    stationList = getStations(ftp, dataType, targetFileBase)
    for station in stationList:
        print(f"working for {station} on {dataType}")
        # get data and extract it
        extractZipFile(ftp, startDate, endDate, station, dataType, targetFileBase, mapFunction, columnNames)

    # clean up
    ftp.close()



if __name__ == '__main__':
    print("INFO: this file is intended to be used as framework for dwd data processing only - use function startup")