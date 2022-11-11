# LatLng 

## Accuracy

http://wiki.gis.com/wiki/index.php/Decimal_degrees

decimal places  degrees	distance
0	1.0	        111 km
1	0.1	        11.1 km
2	0.01	    1.11 km
3	0.001	    111 m
4	0.0001	    11.1 m
5	0.00001	    1.11 m
6	0.000001	0.111 m
7	0.0000001	1.11 cm
8	0.00000001	1.11 mm

# MGRS

https://en.wikipedia.org/wiki/Military_Grid_Reference_System
https://www.maptools.com/tutorials/mgrs/quick_guide

mgrs_level  example                 description
mgrs_2      4Q                      GZD only, precision level 6° × 8° (in most cases)
mgrs_4      4QFJ                    GZD and 100 km Grid Square ID, precision level 100 km
mgrs_6      4QFJ 1 6                precision level 10 km
mgrs_8      4QFJ 12 67              precision level 1 km
mgrs_10     4QFJ 123 678            precision level 100 m
mgrs_12     4QFJ 1234 6789          precision level 10 m
mgrs_14     4QFJ 12345 67890        precision level 1 m

## Accuracy and relation to LatLng decimal reference system

0.0001     degrees ~~ 11.100 km ~~ mgrs_6
0.00001    degrees ~~ 1.1100 km ~~ mgrs_8
0.000001   degrees ~~ 0.1110 km ~~ mgrs_10
0.0000001  degrees ~~ 0.0111 km ~~ mgrs_12


# Geospatial operations

https://stackoverflow.com/questions/32370485/convert-radians-to-degree-degree-to-radians
https://stackoverflow.com/questions/43892459/check-if-geo-point-is-inside-or-outside-of-polygon

## European NUTS classification

https://ec.europa.eu/eurostat/web/nuts/background
https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:NUTS
http://nuts.geovocab.org/
https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Regional_accounts_-_an_analysis_of_the_economy_for_NUTS_level_3_regions


# Political Administrative Levels  

To allow us to sort and filter entities we've set a 4 level classification (same than google places adress_components geocode response)

Political Administrative Levels `PAL` will be the following ones:
- country used as `country` `short` and allways using the abbreviation.
- administrative_area_level_1 used as `aal1` `long`
- administrative_area_level_2 used as `aal2` `long`
- locality used as `locality` `long`

View more: https://developers.google.com/maps/documentation/geocoding/overview#Types

# Other sources

https://en.wikipedia.org/wiki/Latitude
https://en.wikipedia.org/wiki/Geocode
https://en.wikipedia.org/wiki/Open_Location_Code
https://en.wikipedia.org/wiki/Geohash
https://en.wikipedia.org/wiki/Geo_URI_scheme#Uncertainty
https://github.com/google/open-location-code

https://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf
http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
https://github.com/jfein/PyGeoTools/blob/master/geolocation.py
https://www.usna.edu/Users/oceano/pguth/md_help/html/approx_equivalents.htm
