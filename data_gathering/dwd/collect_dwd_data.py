import csv
import datetime
import os
import re


# Directory where the raw text files are located (relative to the base directory)
RAW_TEXT_FILES = '/raw/txt'

# Regex pattern for file name of data file (see iterate_weatherdata.py and dwd_extractor.py)
CSV_FILE_PATTERN = r'^(\d{5})_(.*)\.csv$'

# Mapping of data types to their corresponding attributes
SOURCE_DATA = { 'TU' : ['temperature', 'moisture'],
                'N'  : ['cloudiness'],
                'RR' : ['downfall_height', 'downfall_indicator', 'downfall_type'],
                'SD' : ['sunshine_duration'],
                'VV' : ['visibility'],
                'FF' : ['wind_speed', 'wind_direction'] }



def getAllAttributes():
    """
    Get all relevant attribute names from the SOURCE_DATA. 

    Combine all attributes data týpe by data type

    Args:
    - None
    Returns:
    - list of all attribute names
    """

    relevantAttributes = []
    for src in SOURCE_DATA.values():
        relevantAttributes.extend(src)
    return relevantAttributes



def getAllRelevantStations(baseDir):
    """
    Get all relevant stations from base directory.

    Read all directory names below base directory.

    Args:
    - baseDir: directory to search for station directories
    Returns:
    - list of all stations (station ids)
    """

    relevantStations = []
    dirs = os.listdir(baseDir)
    for dir in dirs:
        if (os.path.isdir(baseDir + '/' + dir)):
            relevantStations.append(dir)
    return relevantStations


def workOnSingleFile(resultData, dateList, stationList, attribs, stationDir, file, stationId, type):
    """
    Process one file.

    read through one station-datatype-measured-value file and update the resultData matrix. 
    In the current implementation, all measured values of one type are displayed next to each other 
    in ascending order of the stations, then all measured values of the next type 
    (W1/Station1,W1/Station2,...W2/Station1,W2/Station2, ...)

    Args:
    - resultData: initialized and pre-populated resultData matrix
    - dateList: list of date-hours (yyyymmddhh)
    - stationList: list of station-ids
    - attribs: list of attributes
    - stationDir: the path of the data files
    - file: the data file to process
    - stationId: the station id (extracted from the filename)
    - type: the data type (extracted from the filename)
    Returns:
    - updated resultData matrix
    """

    fullFilename = stationDir + '/' + file # make full qualified file name for station data file
    currentDataColumns = SOURCE_DATA[type] # get data columns for the specified data type
    
    headerIdxMap = [] # mapping between column here and relative column in result matrix

    # iterate through the station data file for this type
    with open(fullFilename, 'r', encoding='cp1252') as csvFile:
        reader = csv.reader(csvFile)
        first = True
        for row in reader:
            if first: # header line, so create attribute name index mapping
                colIdx = 0
                for headerCol in row:
                    if (colIdx >= 3): # ignore station id, date and hour column
                        headerIdxMap.append(attribs.index(headerCol))
                    colIdx += 1
            else:
                # station, date, hour are always the first three columns
                currentStation = row[0]
                currentStationIdx = stationList.index(currentStation)
                currentDate = row[1]
                currentHour = row[2]
                currentDateIdx = dateList.index(currentDate + currentHour) + 1
                colIdx = 3
                for colIdx in range(3, 3 + len(currentDataColumns)): # iterate over all attributes for this type
                    attrIdx = headerIdxMap[(colIdx-3)] # calc position of attribute in global attribute list
                    value = row[colIdx]
                    
                    # calc column in complete result data matrix - all measured values of same type are in adjacent 
                    # columns, respective stations within the measured values in ascending order
                    cellColIdx = 2 + (attrIdx * len(stationList) + currentStationIdx) 

                    resultDataRow = resultData[currentDateIdx]
                    resultDataRow[cellColIdx] = value
            first = False
    return resultData



def workOnAllFiles(resultData, baseDir, dateList, stationList, attribs):
    """
    Process all files for all stations.

    read through all files in all station directories in baseDir and update the
    resultData matrix.

    Args:
    - resultData: initialized resultData matrix
    - baseDir: directory to read station data from
    - dateList: list of date-hours (yyyymmddhh)
    - stationList: list of station-ids
    - attribs: list of attributes
    Returns:
    - updated resultData matrix
    """

    cnt = 0
    cntStation = 0

    # iterate over all of the stations (assume the data in <basedir>/<station> directory)
    for station in stationList:
        print(f"working on station {station}, {cntStation}/{len(stationList)}")
        stationDir = baseDir + '/' + station
        # get all data files from station directory and iterate over them
        files = os.listdir(stationDir)
        for file in files:
            # extract station number and data type stored in file
            match = re.match(CSV_FILE_PATTERN, file)
            if match: # if it is a data file, process it
                resultData = workOnSingleFile(resultData, dateList, stationList, attribs, stationDir, file, match.group(1), match.group(2))
            cnt = cnt + 1
        cntStation += 1
    print(f"number of files: {cnt} for {cntStation} stations")
    return resultData



def createDateList(startDate, endDate):
    """
    Create a list of date-hour combinations within a given range.

    start at startDate and create one list entry for every day (yyyymmdd) and 
    every hour (00-23) in format yyyymmddhh up to endDate.

    Args:
    - startDate: start date as string in gregorian date format yyyymmdd
    - endDate: end date as string in gregorian date format yyyymmdd
    Returns:
    - list of date/hour from startDate 0 o'clock and eneDateall 23 o'clock
    """

    dateList = []
    sD = datetime.datetime.strptime(startDate, '%Y%m%d')
    eD = datetime.datetime.strptime(endDate, '%Y%m%d')
    delta = datetime.timedelta(days=1)
    while sD <= eD:
        for hour in range(24):
            dateList.append(sD.strftime('%Y%m%d')+f"{hour:02}")
        sD += delta
    return dateList



def initResultData(dateList, stationList, attribs):
    """
    Initialize the resultData matrix with header row, all dates and hours in the first
    two columns and -777 in all other cells.

    Args:
    - dateList: list of date-hours (yyyymmddhh)
    - stationList: list of station-ids
    - attribs: list of attributes
    Returns:
    - the initialized resultData matrix
    """

    # rows are date + header lines
    fstLvl = 1 + len(dateList)
    # columns are date, hour and then attribute * stations
    secLvl = 2 + ((len(attribs)) * len(stationList))
    
    # dimension the result set and initialize every cell with -777 (empty intiailized)
    # use date comprehension for initialization
    dataSheet = [[-777 for x in range(secLvl)] for x in range(fstLvl)]

    # ok, so we set the heder text row
    data_row = dataSheet[0]

    # set header for date and hour    
    data_row[0] = 'date'
    data_row[1] = 'hour'

    # dynamically create header text for attribute (TU-0,TU-1,...,N-0,N-1,...)
    attrIDs = []
    for id, val in SOURCE_DATA.items():
        idx = 0
        for t in val:
            attrIDs.append(f"{id}-{idx:01}")
            idx += 1
    
    # set header text for all stations in all attributes (00011/TU-0,00020/TU-0,00044/TU-0,...)
    idx = 2
    for attrID in attrIDs:
        for station in stationList:
            data_row[idx] = f"{station}/{attrID}"
            idx += 1

    # initialize date and hour
    for d in dateList:
        data_row = dataSheet[dateList.index(d) + 1]
        data_row[0] = str(d[0:8])
        data_row[1] = str(d[8:10])
        
    return dataSheet



def writeResultFile(resultFilename, resultData):
    """
    Write the complete result data to a CSV file.

    Args:
    - resultFilename: filename to write to
    - resultData: List of tuples containing station data.
    """

    with open(resultFilename, 'w', newline='', encoding='cp1252') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        for dataLine in resultData:
            csvWriter.writerow(dataLine)



# Main entry point
if __name__ == '__main__':

    # set start and end date
    startDate = '20220101'
    endDate = '20221231'

    # set the base directory for raw text files
    baseDir = '.' + RAW_TEXT_FILES

    # get list of all relevant stations
    stationList = getAllRelevantStations(baseDir)
    #stationList = [ '00011', '00020', '00044', '00053', '00073', 
    #                '00078', '00087', '00090', '00091', '00096', 
    #                '00102', '00103', '00118', '00124', '00125', 
    #                '00130', '00131', '00142', '00150', '00151', 
    #                '00154', '00158', '00161', '00164', '00167', 
    #                '00183', '00191', '00194', '00197', '00198' ]
    stationList.sort()

    # create a list of dates within the specified range
    dateList = createDateList(startDate, endDate)

    # get all relevant attributes
    attribs = getAllAttributes()

    # initialize the resultData matrix
    resultData = initResultData(dateList, stationList, attribs)

    # Process all files for all stations and update the resultData matrix
    resultData = workOnAllFiles(resultData, baseDir, dateList, stationList, attribs)

    # write the resultData matrix to a csv file (named "the_big_one.csv")
    print("writing result file")
    writeResultFile('./the_big_one.csv', resultData)
    print("written")