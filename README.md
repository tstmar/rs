rs.py is the script to extract view counts

compare.py is the script to compare view counts between different timestamp


Usage:

0, install the required liabrary with pip.


1, python rs.py 

(make sure you can acess reelshort.com with browser, if not, then set up vpn firstly.)

the result would be logged into csv files with timestamp as the filename.


2, python compare.py file1.csv file2.csv -o result.csv

e.g. python compare.py movie_views_20250601_104529.csv movie_views_20250601_174838.csv -o test.csv


