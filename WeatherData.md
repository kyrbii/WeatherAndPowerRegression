# Weather Documentation

## Source

BaseURL is `https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/`

## available Data

* *air_temperature* - **yes**
  station_id, date, air temperature in °C and moisture in %
* *cloud_types* - **no**
  no candidate for data at the moment
* *cloudiness* - **yes**
  station_id, date, bedeckungsgrad in 1/8
* *dew_point* - **no**
  no candidate for data at the moment
* *extreme_wind* - **no**
  *peak wind speed* - not necessary, as we use *wind* (for the average wind speed)
* *moisture* - **no**
  heavy data file - but moisture data is already contained in *air_temperature* (in sufficient accuracy)
* *precipitation* - **yes**
  (downfall) - seems there is no precipitation data available :-(
  station_id, date, niederschlagshoehe in mm, niederschlag ja/nein, niederschlagsform
  **hint** analyze data befor use
* *pressure* - **no**
  no candidate for data at the moment
* *soil temperature* - **no**
  no candidate for data at the moment
* *solar* - **no**
* *sun* - **yes**
  station_id, date, hourly sun shine rate in min
* *visibility* - **yes**
  station_id, date, visibility in m
  **hint** maybe alternatve instead of *precipitation*
* *weather phenomena* - **no**
  no candidate for data at the moment
* *wind* - **yes**
  station_id, date, wind speed in m/s, wind direction in degrees (0 based = north)
* *wind_synop* - **no**
  no candidate for data at the moment

##  outline

* ergebnis ist csv (groß und mächtig)
* davor je station ein verzeichnis
* in diesem je informationsart 

/044/airtemp.csv
    044,tu,20221110,01,14.3,72.0
    044,tu,20221110,01,14.3,72.0
    044,tu,20221110,01,14.3,72.0
    044,tu,20221110,01,14.3,72.0
    044,tu,20221110,01,14.3,72.0
/044/wind.csv
    044,wi,20221110,12,180
    044,wi,20221110,12,180    
    044,wi,20221110,12,180
    044,wi,20221110,12,180

all
extract_tu_dwd --start 2022-01-01 --end 2022-12-31 --station 044 --output /044/airtemp.csv


## extract via ftp

### we know

* start-date
* end-date
* station
* type

### we do

* ftp login
* `cwd('/climate_environment/CDC/observations_germany/climate/hourly/air_temperature')`
* list historical directory (`RETR LIST`)
