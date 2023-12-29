import dwd_extrator

def call_function():
    short_types = ['TU','N','RR','SD','VV','FF']
    full_types = ['air_temperature','cloudiness','precipitation','sun','visibility','wind']
    i = 0
    dwd_extrator(short_types[i], full_types[i], map_TU, ['temperature','moisture'] )
    i+=1
    dwd_extrator(short_types[i], full_types[i], map_N, ['cloudiness'] )
    i+=1
    dwd_extrator(short_types[i], full_types[i], map_RR, ['downfall_height','downfall_indicator','downfall_type'] )
    i+=1
    dwd_extrator(short_types[i], full_types[i], map_SD, ['sunshine_duration'] )
    i+=1
    dwd_extrator(short_types[i], full_types[i], map_VV, ['visibility'] )
    i+=1
    dwd_extrator(short_types[i], full_types[i], map_FF, ['wind_speed','wind_direction'] )


def map_TU(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = temperature in °C
    # 4 = moisture in %
    # 5 = end of record
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_temperature = float(row[3].strip())
    row_humidity = float(row[4].strip())
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, (row_temperature, row_humidity))
    return (None, None, None, None)




def map_N(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = observation
    # 4 = cloudiness
    # 5 = end of record
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_cloudiness = row[5].strip()
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, row_cloudiness)
    return (None, None, None, None)

def map_RR(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = downfall height in mm
    # 4 = indicator
    # 5 = type of downfalll
    # 6 = end of record
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_downfallheight = float(row[3].strip())
    row_downfallindicator = row[4].strip
    row_downfalltype = row[5].strip
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, (row_downfallheight, row_downfallindicator, row_downfalltype))
    return (None, None, None, None)

def map_SD(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = sunshine duration in min
    # 4 = end of record 
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_sunshine = float(row[3].strip())
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, row_sunshine)
    return (None, None, None, None)

def map_VV(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = observation
    # 4 = visibility in m
    # 5 = end of record 
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_visibility = row[4].strip()
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, row_visibility)
    return (None, None, None, None)

def map_FF(row, station, startdate, enddate):
    # 0 = station id
    # 1 = date and hour
    # 2 = quality
    # 3 = windspeed in m/s
    # 4 = direction in degrees from north
    # 5 = end of record 
    row_stationId = ('00000' + row[0].strip())[-5:]
    row_date = row[1][0:8]
    row_hour = row[1][8:10]
    row_windspeed = row[3].strip()
    row_winddirection = row[4].strip()
    if (row_stationId == station) and (row_date >= startdate) and (row_date <= enddate):
        return (row_stationId, row_date, row_hour, (row_windspeed, row_winddirection))
    return (None, None, None, None)






if __name__ == '__main__':
    call_function()