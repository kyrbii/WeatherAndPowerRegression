import csv
import os
import re

REX = r"(.*)(\d{5})_(\w|\w{2}).csv$"

def search_complete_stations(path, datatype):
    # save the needed station IDs for this iteration
    present_stations = os.listdir(f"{path}")
    station_file_counter = {}

    for station in present_stations:
        if os.path.isdir(f"{path}/{station}"):
            for type in datatype:
                if os.path.isfile(f"./{path}/{station}/{station}_{type}.csv"):
                    if os.path.getsize(f'./{path}/{station}/{station}_{type}.csv') > 100:
                        counter = station_file_counter.get(station, 0)
                        station_file_counter[station] = counter + 1
    
    complete_stations = {}
    for station in present_stations:
        counter = station_file_counter.get(station, 0)
        if counter == 6:
            complete = complete_stations.get(station, "True")
            complete_stations[station] = complete
    return complete_stations


        

def startup():
    path = "./../raw/txt"
    datatype = [
        "TU",
        "N",
        "RR",
        "SD",
        "VV",
        "FF"
    ]
    complete_stations = search_complete_stations(path, datatype)
    # print(complete_stations)
    # print(f"Length: {len(complete_stations)}")
    return list(complete_stations.keys())
    pass


if __name__ == "__main__":
    print("Called as main!")
    startup()