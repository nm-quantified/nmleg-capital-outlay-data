# New Mexico Legislature Capital Outlay Scraping 

## Data 

The original data is in PDF form and is available from nmlegis.gov [here](https://nmlegis.gov/Publications/Capital_Outlay/HB%20285%20Capital%20Projects%20Publication%20by%20County%20with%20Sponsor,%202021.pdf)

The ouput of this in csv form is available [here](https://nmlegis.s3-us-west-2.amazonaws.com/HB_285_Capital_Projects_2021.csv)


## Usage

with virtualenv

```
virtualenv venv --python python3
. venv/bin/activate
pip install -r requirements.txt
python scrape.py
```