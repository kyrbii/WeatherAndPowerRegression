import csv, math

def calc_dayiness() -> {}:
    dayiness = {}
    # minus-cosinus function 
    # divide Day
    # pi divided by twelve would be the representetive value in our cosinus wave for 1 hour 
    for hours in range(24):
        if hours < 10:
            dayiness[f"0{hours}"] = -1 * math.cos(hours * ((math.pi)/12))
        else:
            dayiness[f"{hours}"] = -1 * math.cos(hours * ((math.pi)/12))
    # print(dayiness)
    return dayiness

def read_data(csv_type, path_ff_weather, dim_weather, path_ff_power, dim_power, dayiness):
    data = [[None]*dim_weather for number in range(8761)]
    # print(f"ANFANG{data[0]}ENDE{len(data[0])}")
    # think of letting the third row free for the dayiness column
    first = True
    with open(path_ff_weather, "r", newline="") as csv_file:
        filereader = csv.reader(csv_file, delimiter=",")
        
        for ix,row in enumerate(filereader):
            
            # if first:
            #     first = False
            #     continue
            for element in range(len(row)):
                data[ix][element] = row[element]    
            # data[ix - 1] = row
        
        for record in data:
            if first:
                    first = False
                    continue
            record.insert(2, f"{dayiness[record[1]]}")
    
    first = True
    with open(path_ff_power, "r", newline="") as csv_file:
        # print(data[0])
        filereader = csv.reader(csv_file, delimiter=",")        
        for ix, row in enumerate(filereader):
                # if row[csv_type[1]] != "15444/FF-1":
                data[ix][1415] = f"{row[csv_type[1]]}"


    print(f"ANFANG{data[0]}ENDE{len(data[0])}")

    return data

def write_to_csv(path_saving, dim_weather_p2, data):
    pass


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

    for type in csv_types.items():
        write_to_csv(path_saving, dim_weather_p2,read_data(list(type), path_weather, dim_weather_p2, path_power, dim_power, dayiness))
        exit()
    # build a dictionary that crates a negative cosinus style mapping of the daytimeour: dayiness
    


if __name__ == "__main__":
    startup()