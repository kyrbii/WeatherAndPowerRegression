import requests
import os

def startup(time_codes):
    headers = {
        'Accept': 'application/json, text/plain, */*',
    }
    # startDate = '20220101' alias
    # endDate = '20221231' alias
    # Sommerzeit (GMT+2) 2022 in Deutschland Von Sonntag, 27. März 02:00 Uhr bis Sonntag, 30. Oktober  03:00 Uhr
    # https://www.smard.de/app/chart_data/1225/DE/1225_DE_hour_1534716000000.json
    #
    short_power = ['4068','4071','4067','4069','1225','1223','1226','1224','1227','4066','4070','1228','410']
    
    for short_code in short_power:
        os.makedirs(f'./raw/{short_code}', mode=0o777, exist_ok=True)
        for timecode in time_codes:
            request_and_save_json(headers, timecode, short_code)

def request_and_save_json(headers, time_code, short_code):
    print(f'saving {short_code} -> {time_code}')
    response = requests.get(f'https://www.smard.de/app/chart_data/{short_code}/DE/{short_code}_DE_hour_{time_code}.json', headers=headers)
    file2create = open(f'./raw/{short_code}/{time_code}.json', 'w')
    file2create.write(f'{response.json()}')
    file2create.close()
    print(f'saved and closed {short_code} -> {time_code}')

if __name__ == '__main__':
    time_codes = [
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
    startup(time_codes)


