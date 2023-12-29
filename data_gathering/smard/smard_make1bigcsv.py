import csv

def startup(shortys, DICT_shortys):
    data = [[]]
    dimension_counter = int(2)
    create_power_csv(shortys, DICT_shortys)
    for short in shortys:
        readnstore_shorty_csv(short, data, dimension_counter)
        dimension_counter += 1
    write_in_power_csv(data)
    pass
def create_power_csv(shortys, DICT_shortys):
    shortdicts = ['date','hour']
    shortdicts.extend(DICT_shortys.values())
    # change path afterwards to localize the data
    with open('./raw/power2022.csv', 'w') as csv_file:
        start_row = csv.writer(csv_file, delimiter=',', quotechar='\'')
        start_row.writerow(shortdicts)

def readnstore_shorty_csv(short, data, dimension_counter):
    with open(f'./raw/{short}/{short}.csv', newline='') as open_csv:
        csvreader = csv.reader(open_csv, delimiter=',', quotechar='\'')
        counter = int(0)
        first = True
        for row in csvreader:
            if first:
                first = False
                continue
            data[dimension_counter][counter] = row[1]
            data[0][counter] = row[0]
            counter += 1
        pass
    pass

def write_in_power_csv():
    pass






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
    
    # shortys = [ '4068',
    #             '1226']
    # DICT_shortys = {'4068':'solar',
    #                 '1226':'hydro'}
    
    startup(shortys, DICT_shortys)