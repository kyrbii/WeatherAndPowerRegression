# Power Documentation

Here all the files, that smard.de requests as we try to gather the data for power production, are displayed.

On top of this, our procedure is documented.


## page-filter-configuration

First a POST for `page-filter-configuration` is issued with form-urlencoded parameters and returns nothing ()

* item as key/value `contentbean:78`
* filterConfigData as json:
```json
[ { "name":"marketData",
    "data": { "resolution":"hour",
              "from":1703026800000,
              "to":1703113199999,
              "moduleIds":[1004068],
              "selectedCategory":null,
              "activeChart":true,
              "style":"color",
              "categoriesModuleOrder":{},
              "region":"DE" } } ]
```
* `from` and `to` are given as Unix Epoch (eg. 1703026800000 equals GMT Tuesday, 19. December 2023 23:00:00 or our time zone (EST): Mittwoch, 20. Dezember 2023 00:00:00 GMT+01:00)
* `moduleIds` seems to be an array of ids for different sources:
    * `4068` for solar power (prefix `100`)
    * `4071` natural gas
    * `4067` wind onshore
    * `4069` coal
    * `1225` wind offshore
    * `1223` brown coal
    * `1226` hydro power
    * `1224` nuclear power
    * `1227` other conventional
    * `4066` biomass
    * `4070` pumped storage 
    * `1228` other renewables
    * `0410` for whole consumption (prefix `500`)

## index_hour.json

Next a GET for `index-hour.json` is issued and returns all stored interval starts. An interval seems to be one week (7 days).
First possible (at the moment of writing 2023-12-28) is  29. Dezember 2014 00:00:00, last possible is 25. Dezember 2023 00:00:00 starting with monday dates.

```json
{
    "timestamps": [
        1419807600000,
        1420412400000,
        1421017200000,
        1421622000000,
        ....
        1702249200000,
        1702854000000,
        1703458800000
    ]
}

```

## data files

For every source a couple of data files `<moduleId>_DE_hour_<timestamp>.json` is requested.
Timestamps are timestamps from `index_hour.json` (monday starts in Epoch time).

Every data file consists of a header (`meta_data`) with version and creation timestamp and an array `series` with 180 data points (tuple of `timestamp` and `value`).

**Sample file `4068_DE_hour_1703458800000.json`**:

```json
{
    "meta_data": {
        "version": 1,
        "created": 1703763445661
    },
    "series": [
        [
            1703458800000,
            0.0
        ],
        [
            1703462400000,
            0.0
        ],
        ...
              [
            1703595600000,
            3966.25
        ],
        [
            1703599200000,
            1279.75
        ],
        [
            1703602800000,
            48.5
        ],
        ....
```

**Analysis**

* from the filename:
    * data for solar power (filename prefix `4068`)
    * data for region Germany (`DE`)
    * data in hourly resolution
    * data for the week starting Monday, 25. Dezember 2023 00:00:00 GMT+01:00

    **remember:** the filename is originally a request path, so this information is already 
    part of the request

* the content (i.e. the response to the request)
    * `metadata`
        * the version seems to be always `1`
        * when the content was created (Donnerstag, 28. Dezember 2023 12:37:25.661 GMT+01:00)
    * `series`
        * data series is an array of 168 (1 per 24 hours per 7 days) value arrays with two values each - timestamp and power production in MWh
        * so at 1703599200000 (2023-12-26, 15:00 (GMT+1)) the power production was 1279.75 MWh
    * as a result: on 26-12-2023 in the hour between 15:00 an 16:00 1279.75 MWh solar power was produced in Germany
