import csv, math
import csv_dayiness_compact

def calc_dayiness() -> {}:
    dayiness = {}
    # minus-cosinus function 
    # divide Day
    # pi divided by twelve would be the representetive value in our cosinus wave for 1 hour 
    for hours in range(24):
        if hours < 10:
            # rounded for convenience
            dayiness[f"0{hours}"] =round( -1 * math.cos(hours * ((math.pi)/12)), 2)
        else:
            dayiness[f"{hours}"] = round(-1 * math.cos(hours * ((math.pi)/12)), 2)
    return dayiness

def read_data(csv_type, path_ff_weather, dim_weather, path_ff_power, dim_power, dayiness):
    data = [[None]*dim_weather for number in range(8761)]
    first = True
    # read the weather data into the array
    with open(path_ff_weather, "r", newline="") as csv_file:
        filereader = csv.reader(csv_file, delimiter=",")
        
        for ix,row in enumerate(filereader):
            
            for element in range(len(row)):
                data[ix][element] = row[element]    
        # insert a 3rd column to acommodate the dayiness
        for record in data:
            if first:
                    first = False
                    record.insert(2, "dayiness")        
                    continue
            record.insert(2, f"{dayiness[record[1]]}")
    # read the power data into the last row of the array
    first = True
    with open(path_ff_power, "r", newline="") as csv_file:
        # print(data[0])
        filereader = csv.reader(csv_file, delimiter=",")        
        for ix, row in enumerate(filereader):
                data[ix][1416] = f"{row[csv_type[1]]}"
    # print(f"ANFANG{data[0]}ENDE{len(data[0])}")
    return data

def write_to_csv(path_saving, csv_type, dim_weather_p2, data):
    # write the array into an csv
    with open(f"{path_saving}//compact_{csv_type[0]}.csv", "w", newline="") as csv_file:
         alan_wake = csv.writer(csv_file, delimiter=",")
         alan_wake.writerows(data)


def startup():
    csv_types = {"solar":2,
                 "wind_onshore":4,
                 "wind_offshore":5
                }
    path_power = "..//smard//power2022.csv"
    dim_power = 15
    path_weather = "..//dwd//dwd_csvs//data_dwd_wo_RR.csv"
    dim_weather_p2 = 1415 + 1
    path_saving = "."
    dayiness = calc_dayiness()

    # New csv for every type of power production in csv_types
    for type in csv_types.items():
        print(f"creating file for {list(type)[0]}")
        write_to_csv(path_saving, list(type), dim_weather_p2,read_data(list(type), path_weather, dim_weather_p2, path_power, dim_power, dayiness))
    # build a dictionary that crates a negative cosinus style mapping of the daytimeour: dayiness
    


if __name__ == "__main__":
    startup()