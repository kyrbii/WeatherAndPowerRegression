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
    weather_data = [[None]*dim_weather for number in range(8760)]
    # think of letting the third row free for the dayiness column
    first = True
    with open(path_ff_weather, "r", newline="") as csv_file:
        filereader = csv.reader(csv_file, delimiter=",")
        
        for ix,row in enumerate(filereader):
            if first:
                first = False
                continue
            weather_data[ix - 1] = row
        
        for data in weather_data:
            data.insert(2, f"{dayiness[data[1]]}")

        print(weather_data[0])


def write_to_csv(path_saving, dim_weather_p2, data):    
    pass


def startup():
    csv_types = ["solar", "wind_onshore", "wind_offshore"]
    path_power = "..//smard//power.csv"
    dim_power = 15
    path_weather = "..//dwd//dwd_csvs//data_dwd_wo_RR.csv"
    dim_weather_p2 = 1415 + 2
    path_saving = "."
    dayiness = calc_dayiness()

    for type in csv_types:
        write_to_csv(path_saving, dim_weather_p2,read_data(type, path_weather, dim_weather_p2, path_power, dim_power, dayiness))
    # build a dictionary that crates a negative cosinus style mapping of the daytimeour: dayiness
    


if __name__ == "__main__":
    startup()