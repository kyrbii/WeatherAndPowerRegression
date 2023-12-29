import csv
from ftplib import FTP
import os
import re
from zipfile import ZipFile, Path

DWD_FTP_SERVER = 'opendata.dwd.de'
DWD_DATA_BASE_DIR = '/climate_environment/CDC/observations_germany/climate/hourly/'

DWD_HISTORY_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{2})_([0-9]{5})_([0-9]{8})_([0-9]{8})_hist\.zip)'
DWD_RECENT_FILENAME_PATTERN = '^.*(stundenwerte_([A-Z]{2})_([0-9]{5})_akt\.zip)'

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
            if (match.group(2) == dataType) and (match.group(3) == station) and (match.group(4) <= startDate) and (match.group(5) > startDate):
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


def filterStationData(row, station, startDate, endDate):
    # 0 = station id
    # 1 = date and hour
    # 2 = not interesting
    # 3 = temperature in °C
    # 4 = moisture in %
    # 5 = end of record
    rowStationId = ('00000' + row[0].strip())[-5:]
    rowDate = row[1][0:8]
    rowHour = row[1][8:10]
    rowTemperature = float(row[3].strip())
    rowHumidity = float(row[4].strip())
    if (rowStationId == station) and (rowDate >= startDate) and (rowDate <= endDate):
        return (rowStationId, rowDate, rowHour, rowTemperature, rowHumidity)
    return (None, None, None, None, None)


def extractStationData(stationFiles, targetFileBase, station, startDate, endDate):
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
                                (rowStation, rowDate, rowHour, rowTemperature, rowHumidity) = filterStationData(row, station, startDate, endDate)
                                if (rowStation != None):
                                    if (rowDate + rowHour) > tailDateHour:
                                        stationData.append((rowStation, rowDate, rowHour, rowTemperature, rowHumidity))
                                        tailDateHour = rowDate + rowHour
                            first = False
    return stationData


def writeStationData(stationData, targetFileBase, station, dataType):
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
        csvWriter.writerow(['station','date','hour','temp','humidity'])
        csvWriter.writerows(stationData)
                        


def extractZipFile(startDate, endDate, station, dataDir, dataType, targetFileBase):
    # connect to dwd ftp server
    ftp = FTP(DWD_FTP_SERVER)
    ftp.login()

    stationFiles = getStationFiles(ftp, startDate, endDate, station, dataDir, dataType)
    if (len(stationFiles) > 0):
        downloadZipFile(ftp, dataDir, stationFiles, targetFileBase)
        stationData = extractStationData(stationFiles, targetFileBase, station, startDate, endDate)
        writeStationData(stationData, targetFileBase, station, dataType)
    ftp.close()




def startup():
    stationArray = [ '00003', '00044', '00052', '00071', '00073', '00078', '00091', '00096', '00102', '00106', '00125', '00131', '00142', '00150', '00151', '00154',
                     '00161',
  '00164',
  '00167',
  '00175',
  '00181',
  '00183',
  '00191',
  '00198',
  '00217',
  '00222',
  '00232',
  '00257',
  '00259',
  '00268',
  '00282',
  '00284',
  '00294',
  '00298',
  '00303',
  '00314',
  '00320',
  '00326',
  '00330',
  '00342',
  '00348',
  '00350',
  '00361',
  '00368',
  '00377',
  '00379',
  '00390',
  '00399',
  '00400',
  '00403',
  '00410',
  '00420',
  '00424',
  '00427',
  '00430',
  '00433',
  '00445',
  '00450',
  '00460',
  '00474',
  '00535',
  '00553',
  '00554',
  '00555',
  '00591',
  '00596',
  '00598',
  '00599',
  '00603',
  '00617',
  '00656',
  '00662',
  '00685',
  '00691',
  '00701',
  '00704',
  '00722',
  '00755',
  '00757',
  '00760',
  '00766',
  '00769',
  '00817',
  '00840',
  '00850',
  '00853',
  '00856',
  '00860',
  '00863',
  '00867',
  '00876',
  '00879',
  '00880',
  '00891',
  '00896',
  '00917',
  '00919',
  '00920',
  '00953',
  '00954',
  '00963',
  '00979',
  '00982',
  '00983',
  '00991',
  '00998',
  '01001',
  '01048',
  '01050',
  '01051',
  '01052',
  '01072',
  '01076',
  '01078',
  '01103',
  '01107',
  '01130',
  '01161',
  '01197',
  '01200',
  '01207',
  '01214',
  '01219',
  '01221',
  '01224',
  '01228',
  '01239',
  '01246',
  '01255',
  '01262',
  '01266',
  '01270',
  '01279',
  '01281',
  '01297',
  '01300',
  '01303',
  '01327',
  '01332',
  '01339',
  '01341',
  '01346',
  '01357',
  '01358',
  '01411',
  '01420',
  '01421',
  '01424',
  '01425',
  '01426',
  '01443',
  '01451',
  '01468',
  '01473',
  '01490',
  '01503',
  '01504',
  '01515',
  '01526',
  '01544',
  '01550',
  '01572',
  '01580',
  '01583',
  '01584',
  '01587',
  '01590',
  '01602',
  '01605',
  '01612',
  '01639',
  '01645',
  '01666',
  '01684',
  '01691',
  '01694',
  '01721',
  '01735',
  '01736',
  '01757',
  '01758',
  '01759',
  '01766',
  '01792',
  '01803',
  '01832',
  '01833',
  '01834',
  '01863',
  '01869',
  '01886',
  '01892',
  '01902',
  '01957',
  '01960',
  '01964',
  '01975',
  '01981',
  '02014',
  '02023',
  '02039',
  '02044',
  '02074',
  '02080',
  '02081',
  '02088',
  '02110',
  '02115',
  '02158',
  '02166',
  '02167',
  '02171',
  '02174',
  '02201',
  '02211',
  '02244',
  '02252',
  '02261',
  '02290',
  '02303',
  '02306',
  '02315',
  '02319',
  '02323',
  '02338',
  '02362',
  '02374',
  '02385',
  '02410',
  '02423',
  '02429',
  '02437',
  '02444',
  '02456',
  '02477',
  '02480',
  '02483',
  '02485',
  '02486',
  '02488',
  '02494',
  '02497',
  '02503',
  '02521',
  '02522',
  '02532',
  '02542',
  '02559',
  '02564',
  '02565',
  '02575',
  '02578',
  '02597',
  '02600',
  '02601',
  '02618',
  '02627',
  '02629',
  '02638',
  '02641',
  '02656',
  '02667',
  '02680',
  '02691',
  '02693',
  '02700',
  '02704',
  '02708',
  '02712',
  '02738',
  '02750',
  '02761',
  '02773',
  '02794',
  '02796',
  '02812',
  '02814',
  '02829',
  '02856',
  '02878',
  '02886',
  '02905',
  '02907',
  '02920',
  '02925',
  '02928',
  '02932',
  '02947',
  '02951',
  '02953',
  '02961',
  '02968',
  '02985',
  '03015',
  '03023',
  '03028',
  '03031',
  '03032',
  '03034',
  '03042',
  '03044',
  '03083',
  '03085',
  '03086',
  '03093',
  '03098',
  '03126',
  '03137',
  '03139',
  '03145',
  '03147',
  '03155',
  '03158',
  '03164',
  '03166',
  '03167',
  '03170',
  '03181',
  '03196',
  '03204',
  '03226',
  '03231',
  '03234',
  '03244',
  '03245',
  '03246',
  '03254',
  '03257',
  '03268',
  '03271',
  '03274',
  '03278',
  '03284',
  '03287',
  '03289',
  '03307',
  '03319',
  '03321',
  '03340',
  '03348',
  '03362',
  '03366',
  '03376',
  '03379',
  '03382',
  '03385',
  '03390',
  '03402',
  '03404',
  '03426',
  '03442',
  '03478',
  '03484',
  '03485',
  '03490',
  '03509',
  '03513',
  '03527',
  '03540',
  '03545',
  '03552',
  '03571',
  '03575',
  '03577',
  '03591',
  '03603',
  '03605',
  '03612',
  '03621',
  '03623',
  '03631',
  '03639',
  '03659',
  '03660',
  '03667',
  '03668',
  '03671',
  '03679',
  '03702',
  '03730',
  '03734',
  '03739',
  '03761',
  '03791',
  '03811',
  '03815',
  '03821',
  '03836',
  '03857',
  '03875',
  '03879',
  '03897',
  '03904',
  '03925',
  '03927',
  '03939',
  '03946',
  '03975',
  '03987',
  '04018',
  '04024',
  '04032',
  '04036',
  '04039',
  '04063',
  '04094',
  '04104',
  '04127',
  '04154',
  '04160',
  '04169',
  '04174',
  '04175',
  '04177',
  '04189',
  '04261',
  '04271',
  '04275',
  '04280',
  '04287',
  '04294',
  '04300',
  '04301',
  '04323',
  '04336',
  '04339',
  '04347',
  '04349',
  '04350',
  '04354',
  '04371',
  '04373',
  '04377',
  '04393',
  '04411',
  '04445',
  '04464',
  '04466',
  '04477',
  '04480',
  '04485',
  '04501',
  '04508',
  '04517',
  '04548',
  '04559',
  '04560',
  '04584',
  '04592',
  '04605',
  '04625',
  '04629',
  '04642',
  '04651',
  '04665',
  '04692',
  '04702',
  '04703',
  '04704',
  '04706',
  '04709',
  '04719',
  '04745',
  '04748',
  '04752',
  '04763',
  '04813',
  '04841',
  '04857',
  '04878',
  '04887',
  '04896',
  '04911',
  '04926',
  '04927',
  '04928',
  '04931',
  '04933',
  '04978',
  '04997',
  '05009',
  '05014',
  '05017',
  '05029',
  '05046',
  '05049',
  '05064',
  '05068',
  '05097',
  '05099',
  '05100',
  '05109',
  '05111',
  '05133',
  '05142',
  '05146',
  '05149',
  '05155',
  '05158',
  '05229',
  '05275',
  '05277',
  '05279',
  '05280',
  '05282',
  '05300',
  '05335',
  '05347',
  '05349',
  '05371',
  '05397',
  '05404',
  '05419',
  '05424',
  '05426',
  '05431',
  '05433',
  '05440',
  '05467',
  '05480',
  '05490',
  '05516',
  '05538',
  '05541',
  '05546',
  '05562',
  '05629',
  '05640',
  '05643',
  '05663',
  '05664',
  '05665',
  '05676',
  '05688',
  '05692',
  '05705',
  '05715',
  '05717',
  '05719',
  '05731',
  '05732',
  '05745',
  '05750',
  '05779',
  '05792',
  '05797',
  '05800',
  '05802',
  '05822',
  '05825',
  '05832',
  '05839',
  '05856',
  '05871',
  '05906',
  '05930',
  '05941',
  '06093',
  '06105',
  '06109',
  '06129',
  '06157',
  '06158',
  '06159',
  '06163',
  '06170',
  '06182',
  '06184',
  '06186',
  '06192',
  '06197',
  '06199',
  '06217',
  '06242',
  '06243',
  '06244',
  '06245',
  '06246',
  '06247',
  '06254',
  '06255',
  '06256',
  '06258',
  '06259',
  '06260',
  '06262',
  '06263',
  '06264',
  '06265',
  '06266',
  '06272',
  '06273',
  '06275',
  '06305',
  '06310',
  '06312',
  '06314',
  '06336',
  '06337',
  '06344',
  '06346',
  '06347',
  '07075',
  '07099',
  '07105',
  '07106',
  '07135',
  '07187',
  '07244',
  '07298',
  '07319',
  '07321',
  '07329',
  '07330',
  '07331',
  '07341',
  '07343',
  '07350',
  '07351',
  '07364',
  '07367',
  '07368',
  '07369',
  '07370',
  '07373',
  '07374',
  '07389',
  '07393',
  '07394',
  '07395',
  '07396',
  '07403',
  '07410',
  '07412',
  '07419',
  '07420',
  '07424',
  '07427',
  '07428',
  '07431',
  '07432',
  '13667',
  '13670',
  '13674',
  '13675',
  '13696',
  '13700',
  '13710',
  '13711',
  '13713',
  '13776',
  '13777',
  '13904',
  '13965',
  '14003',
  '15000',
  '15207',
  '15444',
  '15555',
  '15813',
  '19171',
  '19172',
  '19207' ]

    startDate = '20220101'
    endDate = '20221231'
    dataType = 'TU'
    dataDir = 'air_temperature'
    targetFileBase = '.'

    for station in stationArray:
        print(f"working for {station}")
        extractZipFile(startDate, endDate, station, dataDir, dataType, targetFileBase)


if __name__ == '__main__':
    startup()

