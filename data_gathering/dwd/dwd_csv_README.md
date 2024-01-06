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

        Outcome: - All these stations will now be used to make a csv (by modifying the collect_dwd_data.py file)
        '00161', '00164', '00183', '00198', '00232', '00282', '00298', '00303', '00342', '00427', '00433', '00460', '00591', '00596', '00662', '00691', '00701', '00704', '00840', '00853', '00856', '00867', '00880', '00891', '00953', '00963', '01001', '01048', '01078', '01200', '01262', '01270', '01303', '01346', '01358', '01420', '01443', '01468', '01503', '01544', '01550', '01580', '01587', '01605', '01612', '01639', '01684', '01691', '01694', '01757', '01759', '01766', '01832', '01869', '01975', '02014', '02023', '02044', '02115', '02171', '02261', '02290', '02483', '02485', '02559', '02597', '02601', '02638', '02667', '02712', '02794', '02812', '02907', '02925', '02932', '02985', '03015', '03028', '03032', '03086', '03093', '03098', '03126', '03158', '03167', '03196', '03231', '03268', '03287', '03366', '03379', '03631', '03660', '03668', '03730', '03761', '03811', '03821', '03987', '04024', '04104', '04177', '04271', '04336', '04393', '04466', '04501', '04625', '04642', '04745', '04887', '04911', '04928', '04931', '05029', '05100', '05142', '05158', '05347', '05349', '05371', '05397', '05404', '05426', '05440', '05480', '05490', '05516', '05546', '05629', '05705', '05779', '05800', '05839', '05856', '05906', '05930', '06163', '06197', '07341', '07351', '07367', '07368', '07369', '07370', '07374', '07393', '07394', '07395', '07396', '07403', '07410', '07412', '13674', '15000', '15207', '15444'


_Second approach:_\
Only include station that include the following, currently more important data:
```
        to be changed

N-Data              cloudiness

VV-Data             visibility

SD-Data             sunshine

FF-Data             wind
```