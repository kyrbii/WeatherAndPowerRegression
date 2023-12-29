import csv
import time

def startup(shortys, DICT_shortys, start_end):
    #data = [15][9500]
    data = [ ['x']*15 for i in range(8760)]
    dimension_counter = int(2)
    for short in shortys:
        readnstore_shorty_csv(short, data, dimension_counter, start_end)
        dimension_counter += 1
    create_power_csv(shortys, DICT_shortys, data)
    # trim_powercsv(time)
    # line 2 bis line 121 sind zu viel
    # ab line 8882 ist zu viel (1672527600000 ist schon das neue Jahr)


# def trim_powercsv(time):
    # with open(f'./raw/power2022.csv', newline='') as main_csv:
        # reader = csv.reader(main_csv, delimiter=',', quotechar='\'')
        # with open('./raw/temp2022.csv', 'w') as temp_csv:
            # writer = csv.writer(temp_csv, delimiter=',', quotechar='\'', lineterminator='\n')
            # for row in reader:
                # pass

def create_power_csv(shortys, DICT_shortys, data):
    shortdicts = ['date','hour']
    shortdicts.extend(DICT_shortys.values())
    # change path afterwards to localize the data
    with open('./power2022.csv', 'w') as csv_file:
        start_row = csv.writer(csv_file, delimiter=',', quotechar='\'', lineterminator='\n')
        start_row.writerow(shortdicts)
        start_row.writerows(data)

def readnstore_shorty_csv(short, data, dimension_counter, start_end):
    with open(f'./raw/{short}/{short}.csv', newline='') as open_csv:
        csvreader = csv.reader(open_csv, delimiter=',', quotechar='\'')
        counter = int(0)
        first = True
        for row in csvreader:
            if first:
                first = False
                continue
            if start_end[0]<=int(row[0]) and start_end[1]>=int(row[0]):
                data[counter][dimension_counter] = row[1]
                date = time.localtime(float(row[0])/1000)
                data[counter][0] = f'{date[0]:04}{date[1]:02}{date[2]:02}'
                data[counter][1] = f'{date[3]:02}'
                counter += 1






if __name__ == '__main__':

    shortys = [ '4068',
                '1226',
                '4067',
                '1225',
                '1224',
                '4071',
                '4069',
                '1223',
                '4066',
                '1227',
                '1228',
                '4070',
                '410'
                ]
    
    DICT_shortys = {'4068':'solar',
                    '1226':'hydro',
                    '4067':'wind_onshore',
                    '1225':'wind_offshore',
                    '1224':'nuclear',
                    '4071':'natural_gas',
                    '4069':'coal',
                    '1223':'brown_coal',
                    '4066':'biomass',
                    '1227':'other_conventional',
                    '1228':'other_renewables',
                    '4070':'pumped_storage',
                    '410':'power_consumption_germany'
                    }
    start_end = [1640991600000,1672524000000]
    
    # shortys = [ '4068',
    #             '1226']
    # DICT_shortys = {'4068':'solar',
    #                 '1226':'hydro'}
    
    startup(shortys, DICT_shortys, start_end)