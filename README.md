# Switzerland's Real Estate Scraper

This Python script allows you to scrape real estate data from [homegate.ch](https://www.homegate.ch/), a real estate website in Switzerland. The script provides options to filter properties based on various criteria such as advertisement type, city, number of rooms, year built, living space, and price range. It scrapes the search results page, extracts information about each property, and returns details such as price, location, number of rooms, living space area, year built, and ddditional details about the advertiser, contact information, and more.
The script also saves each property item in a MongoDB database for future reference and analysis, and generates plots based on the scraped data, illustrating distributions and relationships between key numeric columns.

## Prerequisites

- Python 3.x
- `beautifulsoup4` package
- `requests` package
- `selenium` package
- `matplotlib` package
- `pandas` package
- `pymongo` package

## Usage

- Clone the Repository:

    ```bash
    git clone https://github.com/FatemehCh97/Real-Estate-Scraper.git
    ```

- Install the required packages by running the following command:

    ```bash
    pip install -r requirements.txt
    ```

- Ensure MongoDB is installed and running.
- Update the MongoDB connection details in in local_settings.py (according to sample_settings.py)
- Use the following command to run the script:

```
python main.py -t [buy or rent] -c [city1] [city2] ... [cityN] -rf [rooms_from] -rt [rooms_to] -yf [year_from] -yt [year_to] -pf [price_from] -pt [price_to] -r
```

Replace the placeholders ([...]) with your desired values. Here are some examples:

To search for rental properties in Zurich and Geneva with 3 rooms (and plotting the charts):
```
python main.py -t rent -c Zurich Geneva -rt 3 -r
```
To search for properties for sale in Basel with a minimum price of 500,000 CHF:
```
python main.py -t buy -c Basel -pf 500000 -r
```

**Options**

-t, --type: Advertisement type (buy or rent, required).
-c, --cities: List of city names (at least one city is required).
-rf, --rooms_from: Number of rooms (from).
-rt, --rooms_to: Number of rooms (to).
-yf, --year_from: Year built (from).
-yt, --year_to: Year built (to).
-sf, --space_from: Living space (from).
-st, --space_to: Living space (to).
-pf, --price_from: Minimum price.
-pt, --price_to: Maximum price.
-r, --report: Print plots based on the scraped data.
