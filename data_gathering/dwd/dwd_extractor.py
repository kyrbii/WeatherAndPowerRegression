import csv
from ftplib import FTP
from io import BytesIO
import os
import re
from zipfile import ZipFile, Path

DWD_FTP_SERVER = 'opendata.dwd.de'
DWD_DATA_BASE_DIR = '/climate_environment/CDC/observations_germany/climate/hourly/'

DWD_HISTORY_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{1,2})_([0-9]{5})_([0-9]{8})_([0-9]{8})_hist\.zip)'
DWD_RECENT_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{1,2})_([0-9]{5})_akt\.zip)'
DWD_STATION_LIST_PATTERN = '^(\d{5})\s+(\d{8})\s+(\d{8})\s+(-?\d{1,4})\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(.*?)\s+([A-ZÄÖÜa-zäöü-]+)\s+$'

HISTORY_PATH = 'historical'
RECENT_PATH = 'recent'
RAW_DATA_PATH = '/raw/zip/'
TXT_DATA_PATH = '/raw/txt/'

def getRelevantHistoryFilename(filenames, station, dataType, startDate):
    stationFile = ''
    for filename in filenames:
        match = re.match(DWD_HISTORY_FILENAME_PATTERN, filename)
        if match:
            # group(2) -> typ (TU)
            # group(3) -> station
            # group(4) -> s
            # group(5) -> e
            # s <= startDate    und    e >= endDate -> nur historie
            # s <= startDate    und    e < endDate -> historie + aktuell
            # e <= startDate -> nicht historie
            if (match.group(2) == dataType) and (match.group(3) == station) and (match.group(5) > startDate):
                stationFile = filename
    return stationFile



def getFilteredRecentFilename(filenames, filename, station, dataType):
    match = re.match(DWD_RECENT_FILENAME_PATTERN, filename)
    if match:
        if (match.group(2) == dataType) and (match.group(3) == station):
            filenames.append(match.group(1))

def getRecentFilename(ftp, station, dataDir, dataType):
    ftp.cwd(DWD_DATA_BASE_DIR)
    ftp.cwd(dataDir)
    ftp.cwd(RECENT_PATH)
    # get all filenames
    filenames = []
    ftp.dir(lambda filename: getFilteredRecentFilename(filenames, filename, station, dataType))
    if len(filenames) > 0:
        return filenames[0]
    return ''



def getStationFiles(ftp, startDate, endDate, station, dataDir, dataType):
    # go to the base dir for hourly observation data for germany
    ftp.cwd(DWD_DATA_BASE_DIR)
    # we extract data for air_temperature <--- this can vary depending on data type
    ftp.cwd(dataDir)

    # first check historical data
    ftp.cwd(HISTORY_PATH)
    # get all filenames
    filenames = []
    ftp.dir(filenames.append)
    # get relevant ones
    historyFile = getRelevantHistoryFilename(filenames, station, dataType, startDate)
    stationFiles = []
    # do we have to check recent data?
    if (len(historyFile) > 0):
        match = re.match(DWD_HISTORY_FILENAME_PATTERN, historyFile)
        stationFiles.append(match.group(1))
        if match.group(5) < endDate:
            fileName = getRecentFilename(ftp, station, dataDir, dataType)
            if len(fileName) > 0:
                stationFiles.append(fileName)
    else:
        fileName = getRecentFilename(ftp, station, dataDir, dataType)
        if len(fileName) > 0:
            stationFiles.append(fileName)
    return stationFiles



def downloadZipFile(ftp, dataDir, stationFiles, targetFileBase):
    for stationFile in stationFiles:
        ftp.cwd(DWD_DATA_BASE_DIR)
        ftp.cwd(dataDir)
        if stationFile[-7:] == 'akt.zip':
            ftp.cwd(RECENT_PATH)
        else:
            ftp.cwd(HISTORY_PATH)
        try:
            os.makedirs(targetFileBase + RAW_DATA_PATH)
        except FileExistsError:
            pass
        with open(targetFileBase + RAW_DATA_PATH + stationFile, 'wb') as downloadFile:
            ftp.retrbinary(f"RETR {stationFile}", downloadFile.write)



def extractStationData(stationFiles, targetFileBase, station, startDate, endDate, mapFunction):
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
    try:
        os.makedirs(targetFileBase + TXT_DATA_PATH + station)
    except FileExistsError:
        pass
    filename = targetFileBase + TXT_DATA_PATH + station + '/' + station + '_' + dataType + '.csv'
    try:
        os.remove(filename)
    except:
        pass
    with open(filename, 'w') as csvFile:
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
                        


def extractZipFile(ftp, startDate, endDate, station, dataDir, dataType, targetFileBase, mapFunction, columnNames):
    stationFiles = getStationFiles(ftp, startDate, endDate, station, dataDir, dataType)
    if (len(stationFiles) > 0):
        downloadZipFile(ftp, dataDir, stationFiles, targetFileBase)
        stationData = extractStationData(stationFiles, targetFileBase, station, startDate, endDate, mapFunction)
        writeStationData(stationData, targetFileBase, station, dataType, columnNames)



def getStations(ftp, dataDir, dataType, targetFileBase):
    listOfAllStations = []
    data = BytesIO()
    # first historical
    stationListFile = DWD_DATA_BASE_DIR + dataDir + '/' + HISTORY_PATH + '/' + dataType + '_Stundenwerte_Beschreibung_Stationen.txt'
    try:
        ftp.retrbinary(f'RETR {stationListFile}', data.write)
    except:   
        stationListFile = DWD_DATA_BASE_DIR + dataDir + '/' + RECENT_PATH + '/' + dataType + '_Stundenwerte_Beschreibung_Stationen.txt'
        try:
            print("reading recent")
            ftp.retrbinary(f'RETR {stationListFile}', data.write)
        except:
            data = None
    if data:
        print(f"writing to {targetFileBase + TXT_DATA_PATH + dataType + '_stations.csv'}")
        with open(targetFileBase + TXT_DATA_PATH + dataType + '_stations.csv', 'w', encoding='cp1252') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter=',')
            csvWriter.writerow(['station','date_from','date_to','altitude','longitude','lattitude','name','state'])
            data_as_str = data.getvalue().decode('cp1252')
            data_as_array = data_as_str.split('\r\n')
            line_cnt = 0
            for data_line in data_as_array:
                if line_cnt > 2:
                    if (len(data_line) > 0):
                        match = re.match(DWD_STATION_LIST_PATTERN, data_line)
                        listOfAllStations.append(match.group(1))
                        csvWriter.writerow([match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6), match.group(7), match.group(8)])
                line_cnt += 1
    return listOfAllStations



def startup(dataType, dataDir, mapFunction, columnNames):

    startDate = '20220101'
    endDate = '20221231'

    # connect to dwd ftp server
    ftp = FTP(DWD_FTP_SERVER)
    ftp.login()
    targetFileBase = '.'

    stationList = getStations(ftp, dataDir, dataType, targetFileBase)
    for station in stationList:
        print(f"working for {station} on {dataType}")
        extractZipFile(ftp, startDate, endDate, station, dataDir, dataType, targetFileBase, mapFunction, columnNames)

    ftp.close()


if __name__ == '__main__':
    startup()

