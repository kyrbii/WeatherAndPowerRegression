import csv
import datetime
import os
import re


RAW_TEXT_FILES = '/raw/txt'

CSV_FILE_PATTERN = "^(\d{5})_(.*)\.csv$"

SOURCE_DATA = { 'TU' : ['temperature', 'moisture'],
                'N'  : ['cloudiness'],
                'RR' : ['downfall_height', 'downfall_indicator', 'downfall_type'],
                'SD' : ['sunshine_duration'],
                'VV' : ['visibility'],
                'FF' : ['wind_speed', 'wind_direction'] }

# welche attribute
# entsprechendes array aufbauen
# header konstruieren und füllen
# datum uhrzeit spalte füllen
# alle dateien einlesen
# für alle Stationen
#   für alle Dateien
#     extrahieren typ aus dateiname
#     für alle Sätze aus Datei
#       ermittle datums, uhrzeit, station, attribute und fülle in array
# schreibe array als csv datei
# /<station>/<station>_<typ>.csv

def getAllAttributes():
    # relevantAttributes = ['station', 'date', 'hour']
    relevantAttributes = []
    for src in SOURCE_DATA.values():
        relevantAttributes.extend(src)
    return relevantAttributes




def getAllRelevantStations(baseDir):
    relevantStations = []
    dirs = os.listdir(baseDir)
    for dir in dirs:
        if (os.path.isdir(baseDir + '/' + dir)):
            relevantStations.append(dir)
    return relevantStations


def workOnSingleFile(resultData, dateList, stationList, attribs, stationDir, file, stationId, type):
    currentDataColumns = SOURCE_DATA[type]
    fullFilename = stationDir + '/' + file
    headerIdxMap = [] # mapping between column here and relative column in result matrix
    with open(fullFilename, 'r', encoding='cp1252') as csvFile:
        reader = csv.reader(csvFile)
        first = True
        for row in reader:
            if first:
                colIdx = 0
                for headerCol in row:
                    if (colIdx >= 3):
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
                for colIdx in range(3, 3 + len(currentDataColumns)):
                    # calc position of attribute in global attribute list
                    attrIdx = headerIdxMap[(colIdx-3)]
                    val = row[colIdx]
                    cellColIdx = 2 + (attrIdx * len(stationList) + currentStationIdx)
                    resultDataRow = resultData[currentDateIdx]
                    resultDataRow[cellColIdx] = val
            first = False
    return resultData



def workOnAllFiles(resultData, baseDir, dateList, stationList, attribs):
    cnt = 0
    cntStation = 0
    for station in stationList:
        print(f"working on station {station}, {cntStation}/{len(stationList)}")
        stationDir = baseDir + '/' + station
        files = os.listdir(stationDir)
        for file in files:
            match = re.match(CSV_FILE_PATTERN, file)
            if match:
                resultData = workOnSingleFile(resultData, dateList, stationList, attribs, stationDir, file, match.group(1), match.group(2))
            cnt = cnt + 1
        cntStation += 1
    print(f"number of files: {cnt} for {cntStation} stations")
    return resultData


def date2julian(gregDateStr):
    return datetime.datetime.strptime(gregDateStr, '%Y%m%d').strftime('%Y%j')



def createDateList(startDate, endDate):
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
    # rows are date + header line
    fstLvl = 1 + len(dateList)
    # columns are date, hour and then attribute times stations
    secLvl = 2 + ((len(attribs)) * len(stationList))
    
    # dimension the result set and initialize every cell with -1
    dataSheet = [[-777 for x in range(secLvl)] for x in range(fstLvl)]

    # ok, so we set the heder text row
    data_row = dataSheet[0]

    # set header for date and hour    
    data_row[0] = 'date'
    data_row[1] = 'hour'

    # dynamically create header text for attribute
    attrIDs = []
    for id, val in SOURCE_DATA.items():
        idx = 0
        for t in val:
            attrIDs.append(f"{id}-{idx:01}")
            idx += 1
    
    # set header text for all stations in all attributes
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
    with open(resultFilename, 'w', encoding='cp1252') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        for dataLine in resultData:
            csvWriter.writerow(dataLine)



if __name__ == '__main__':
    startDate = '20220101'
    endDate = '20221231'
    baseDir = '.' + RAW_TEXT_FILES
    stationList = getAllRelevantStations(baseDir)
    #stationList = [ '00011', '00020', '00044', '00053', '00073', 
    #                '00078', '00087', '00090', '00091', '00096', 
    #                '00102', '00103', '00118', '00124', '00125', 
    #                '00130', '00131', '00142', '00150', '00151', 
    #                '00154', '00158', '00161', '00164', '00167', 
    #                '00183', '00191', '00194', '00197', '00198' ]
    stationList.sort()
    dateList = createDateList(startDate, endDate)
    attribs = getAllAttributes()
    resultData = initResultData(dateList, stationList, attribs)
    resultData = workOnAllFiles(resultData, baseDir, dateList, stationList, attribs)
    print("writing result file")
    writeResultFile('./the_big_one.csv', resultData)
    print("written")