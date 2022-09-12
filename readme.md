## Description

Scraper for collecting data from snpedia.com, in particular for compiling a csv-file of all possible mutations in the human genome, which are found to affect a person according to studies with proven clinical significance.

## Install

Just install the requirements by:
```
pip install -r requirements.txt
```

## Run and use

Create and activate virtual environment, then run the script:
```
python -m venv venv
source venv/bin/activate
python parser.py
```
Deativate virtual environment:
```
deactivate
```

The main function includes sequentially executed functions related to different stages of data collection and processing, which are specified in the function docstrings. You can disable and enable functions by commenting them out inside the main function. Also, when there is a slow or unstable connection, it is possible to start data collection from the moment it stopped. 