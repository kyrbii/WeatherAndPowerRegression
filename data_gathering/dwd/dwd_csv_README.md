# Documentation of the weather data csv files

## the_big_one.csv

The ```the_big_one.csv``` file displays all the information for data types we chose were relevant for the project for all the stations that have published data for all 2022.

### rows

each row represents a hour of the year 2022

### date column

day, in date format `yyyymmdd`

### hour column
hour of the day, when the data was gathered in `24 hour` format

### All other columns

these are all the stations data grouped by *sub-data types*.\
The columns are named `XXXXX/YY-I` where

``XXXXX`` is the station-ID the data was gathered from\
``YY`` is the abbreviation for the type of data\
``I`` is the subtype of data

_A list to specify the abbreviations and sub-types in form `YY-I`:_

```
TU-0    air temperature in °C

TU-1    moisture in %

N-0     cloudiness in 1/8 parts of the sky

RR-0    hourly downfall in mm

RR-1    indicator of downfall in numerical binary code

RR-2    type of downfall in numerical code

SD-0    sunshine per hour in min

VV-0    visibility in m

FF-0    wind speed in m/sec

FF-1    wind direction in degrees from north
```

The file contains columns, where the station didn't measure a single piece of data. The columns were created for the sake of completeness of our data. Therefore for use in our project it likely has to be further curated!

___

### strip the_big_one.csv_
In order to use the weather dataset for our classifier, we need to strip the data. At the moment in our ``the_big_one.csv`` file there are many columns of stations to which we didn't find any data (marked with -777)\
Furthermore there are stations which didn't really collect data, but nontheless wrote it into their txt file. This could be confusing for us while testing and could influence the outcome. But this is an issue that we will face during programming and try to avoid data with value -999/-999.0

First we try to strip the csv / write a different csv where we will have a little less data but it'll be more valuable for our goal!


### stripping
_First approach:_\
Have a look and see which stations offer all of our data! Meaning we will only take the stations into account where we have all 6 csv files in our ``data_gathering/raw/txt/'stations'`` path!

--> dwd_makecsv_fromcompletedata.py


_Second approach:_\
Only include station that include the following, currently more important data:
```
        to be changed

N-Data              cloudiness

VV-Data             visibility

SD-Data             sunshine

FF-Data             wind
```