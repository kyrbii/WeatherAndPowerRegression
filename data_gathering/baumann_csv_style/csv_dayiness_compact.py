# make a more compact csv where we theoretically could maybe create the mean value for the weather data between the stations
import csv_with_dayiness as CWD, csv

def make_stripped_csv(fulldata, type):
    data = [[None]*13 for n in range(8761)]
    start_point = 3
    rem_avg = 0
    cnt = 0
    column = 3
    first = True
    for ix, row in enumerate(fulldata):
        if first:
            first = False
            continue
        column = 3
        start_point = 3
        for j in range(9):
            rem_avg = 0
            cnt = 0
            for i in range(157):
                rem_val = float(row[start_point + i])
                # print(rem_val)
                if rem_val != -777 and rem_val != -999:
                    rem_avg += rem_val
                    cnt+=1
            # print(rem_avg)
            if cnt == 0:
                data[ix][column] = -999
            else:
                data[ix][column] = rem_avg / cnt
            # print(data[ix][column])
            column += 1
            start_point += 157
    data = times_n_power(fulldata, data, type)
    print(data[1])
    return data

def times_n_power(full_data, data, type):
    first = True
    for ix, row in enumerate(full_data):
        if first:
            first = False
            data[ix] = ["date", "hour", "dayiness", "mean_TU_0", "mean_TU_1", "mean_N_0", "mean_RR_0", "mean_RR_1", "mean_SD_0", "mean_VV_0", "mean_FF_0", "mean_FF_1", f"{type[0]}"]
            continue
        data[ix][0] = full_data[ix][0]
        data[ix][1] = full_data[ix][1]
        data[ix][2] = full_data[ix][2]
        data[ix][12] = full_data[ix][1416]
    return data

def main():
    csv_types = {"solar":2,
                 "wind_onshore":4,
                 "wind_offshore":5
                }
    path_power = "..//smard//power2022.csv"
    dim_power = 15
    path_weather = "..//dwd//dwd_csvs//data_dwd_wo_RR.csv"
    dim_weather_p2 = 1415 + 1
    path_saving = "."
    for type in csv_types.items():
        full_data = CWD.read_data(list(type), path_weather, dim_weather_p2, path_power, dim_power, CWD.calc_dayiness())
        stripped = make_stripped_csv(full_data, list(type))
        CWD.write_to_csv(".", list(type),dim_weather_p2,stripped)
if __name__ == "__main__":
    main()
