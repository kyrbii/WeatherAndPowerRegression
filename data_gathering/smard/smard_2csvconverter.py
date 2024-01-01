import csv
import json

def startup(timecodes, shortpowers):
    # bundle the data for each shortcode/powerssource of 2022 into one csv
    for shortpower in shortpowers:
        # obsolete because I changed the command but I like it
        create_csv(shortpower)
        with open(f'./raw/{shortpower}/{shortpower}.csv', 'w', newline='') as csv_file:
            writethis = csv.writer(csv_file, delimiter=',', quotechar='\'')
            # write the header
            writethis.writerow(['time','value'])
            # iterate, so that all the timecode_files are used
            # I just realize I could have iterated in the write json 2 csv function, but it works regardless. Never change a running system
        for timecode in timecodes:
            # write it all into the json
            write_json_2_csv(shortpower, timecode)

def create_csv(shortpower):
    # create a csv file
    with open(f'./raw/{shortpower}/{shortpower}.csv', 'w') as csv_file:
        pass

def write_json_2_csv(shortpower, timecode):
    json_file = open(f'./raw/{shortpower}/{timecode}.json', 'r')
    # modify the json, so that it can be interpreted, as a python file
    json_data = json.loads(json_file.readline().replace("'",'"'))
    json_series = json_data['series']
    # append to the csv file
    with open(f'./raw/{shortpower}/{shortpower}.csv', 'a', newline='') as csv_file:
        writethis = csv.writer(csv_file, delimiter=',', quotechar='\'')
        # write all rows in one command just by writing an iterable array :)
        writethis.writerows(json_series)
    
    json_file.close()


if __name__ == '__main__':
    shortpowers = [
        '4068',
        '4071',
        '4067',
        '4069',
        '1225',
        '1223',
        '1226',
        '1224',
        '1227',
        '4066',
        '4070',
        '1228',
        '410']
    timecodes = [
        1640559600000, 
        1641164400000,
        1641769200000,
        1642374000000,
        1642978800000,
        1643583600000,
        1644188400000,
        1644793200000,
        1645398000000,
        1646002800000,
        1646607600000,
        1647212400000,
        1647817200000,
        1648418400000,
        1649023200000,
        1649628000000,
        1650232800000,
        1650837600000,
        1651442400000,
        1652047200000,
        1652652000000,
        1653256800000,
        1653861600000,
        1654466400000,
        1655071200000,
        1655676000000,
        1656280800000,
        1656885600000,
        1657490400000,
        1658095200000,
        1658700000000,
        1659304800000,
        1659909600000,
        1660514400000,
        1661119200000,
        1661724000000,
        1662328800000,
        1662933600000,
        1663538400000,
        1664143200000,
        1664748000000,
        1665352800000,
        1665957600000,
        1666562400000,
        1667170800000,
        1667775600000,
        1668380400000,
        1668985200000,
        1669590000000,
        1670194800000,
        1670799600000,
        1671404400000,
        1672009200000
    ]
    # testing snippet
    # timecodes = [
    #     1640559600000]
    # shortpowers = [
    #     '4068']
    startup(timecodes, shortpowers)

