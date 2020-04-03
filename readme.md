## Pre-Requisites
Install python virtual environment.
```
sudo apt-get install python3-virtualenv
virtualenv -p /usr/bin/python3.x .venv/
```
For python3.6+, you can create an environment by using:
```
pip3 install venv
python3 -m 'venv .venv/'
```
More information on creating python environments can be [found here.](https://docs.python.org/3/tutorial/venv.html)  Now, activate virtual environment to work in isolation from python globally available.
```
source .venv/bin/activate
```
  
Lastly, install required libraries using requirements file.
```
pip install -r requirements.txt
```
## Usage
To find out all available options.
```
python script.py -h

usage: script.py [-h] [-url URL] [-prefix PREFIX]

optional arguments:
  -h, --help      show this help message and exit
  -url URL        URL to crawl.
  -prefix PREFIX  prefix for csv file.

```
**`-url [URL]`** is an optional parameter which can be any of the following urls.
```
https://www.eia.gov/dnav/ng/hist/rngwhhdd.htm
https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm
https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm (Default)
https://www.eia.gov/dnav/ng/hist/rngwhhda.htm
```
**`-prefix [PREFIX]`** is an optional parameter which specifies the prefix to use for CSV files created to store crawled data.  
  
For example, to start crawling from url `https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm` and write CSV files prefixed with current date, run the following.
```
python script.py -url https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm -prefix "$(date '+%d-%m-%Y')"
```
Response should be similar to this.
```
[2020-04-03 22:30:53,698] Fetching from URL: https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm
[2020-04-03 22:30:55,759] Fetched 4 variants of data.
[2020-04-03 22:30:55,760] Fetching from URL: https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm
[2020-04-03 22:30:59,106] Writing data to file: 03-04-2020_daily.csv
[2020-04-03 22:30:59,111] Using already fetched content of URL: https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm
[2020-04-03 22:30:59,172] Writing data to file: 03-04-2020_weekly.csv
[2020-04-03 22:30:59,174] Fetching from URL: https://www.eia.gov/dnav/ng/hist/rngwhhdM.htm
[2020-04-03 22:31:00,826] Writing data to file: 03-04-2020_monthly.csv
[2020-04-03 22:31:00,827] Fetching from URL: https://www.eia.gov/dnav/ng/hist/rngwhhdA.htm
[2020-04-03 22:31:01,915] Writing data to file: 03-04-2020_annual.csv
```
Note that CSV filenames without any prefix default to `daily.csv`, `weekly.csv`, `monthly.csv` or `annual.csv` depending upon what page is crawled.