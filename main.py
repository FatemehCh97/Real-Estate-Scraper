import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient
import json
import os

import local_settings
from plot_info import plot_property_info
# from get_info import get_property_item_info
from get_info_request import get_property_item_info
from args_url import create_parser, create_url


# Create a MongoDB connection
client = MongoClient(host=local_settings.DATABASE['host'],
                     port=local_settings.DATABASE['port'])

mongodb_database = client[local_settings.DATABASE['name']]

# Check if 'RealEstates' collection exists
if 'RealEstates' in mongodb_database.list_collection_names():
    homes_collection = mongodb_database.get_collection('RealEstates')
else:
    homes_collection = mongodb_database['RealEstates']

base_url = ("https://www.homegate.ch/{ad_type}/real-estate/"
            "city-{city}/matching-list?")
headers = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/50.0.2661.102 Safari/537.36')
}

args = create_parser()

# Build the dynamic file name
city_name = args.cities[0] if args.cities else "UnknownCity"
room_info = (
    f"RoomsFrom{args.rooms_from}To{args.rooms_to}"
    if args.rooms_from or args.rooms_to else "AllRooms"
)
price_info = (
    f"PriceFrom{args.price_from}To{args.price_to}"
    if args.price_from or args.price_to else "AllPrices"
)
year_info = (
    f"YearBuiltFrom{args.year_from}To{args.year_to}"
    if args.year_from or args.year_to else "AllPrices"
)

current_page = 1
df = pd.DataFrame()
while True:

    url = create_url(base_url)

    if current_page == 1:
        url = url
    else:
        # Create the URL for the current page
        url += "&ep={}".format(current_page)

    # Send a request to the URL
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error accessing page {current_page}")
        break

    # Parse the HTML content
    content = BeautifulSoup(response.content, 'html.parser')

    # Check if the naxt page is empty or not
    result_list_a = content.find_all(
        'a', class_="HgCardElevated_content_uir_2 HgCardElevated_link_EHfr7"
        )

    # If there is no properties matching criteria search
    if content.find('div',
                    class_=('NoResultsWarning_noResultsWarning_ACtzU'
                            ' ResultListPage_noResults_GcsiY')):
        if result_list_a:
            print("Other properties you might be interested in based on your "
                  "search criteria")
        else:
            print("Looks like there aren't any properties matching your "
                  "search criteria at the moment.")

    if not result_list_a:
        break

    print(url)

    # Initialize an empty list to store property_info_dict for each property
    property_info_list = []
    # Get URL of each property item found in result and print information
    for property_item in result_list_a:
        result_item_url = property_item['href']
        if result_item_url:
            item_url = "https://www.homegate.ch" + f'{result_item_url}'
            print(item_url)
            # Get information of property item
            property_info_dict = get_property_item_info(item_url)
            # Add property item information (dictionary) to MongoDB
            # Check if the document with the same title already exists
            existing_property = homes_collection.find_one({
                'Title': property_info_dict['Title']
                })

            # If the document doesn't exist, insert it
            if not existing_property:
                homes_collection.insert_one(property_info_dict)
                print("Document added successfully.")
            else:
                print("Document with the same title already exists."
                      " Not adding duplicate.")

            # Create a DataFrame
            selected_keys = ['Price', 'Living Space', 'Rooms']

            # Create DataFrame with selected keys as columns, and their value
            # from scraped property advertise, listing ID of item as index
            df_item = pd.DataFrame({key: [property_info_dict.get(key, None)]
                                    for key in selected_keys},
                                   index=[result_item_url.split('/')[-1]])

            # Add 'Year Built' information to df_item
            df_item['Year Built'] = property_info_dict.get('Main Information', {}).get('Year built', None)

            # Add created DataFrame as a row to df
            df = pd.concat([df, df_item])

            # Append property_info_dict to the list
            property_info_list.append(property_info_dict)
        else:
            print("Element not found.")

    # Combine all the components to create the file name
    file_name = (
        f"Property_{city_name}_{room_info}_{price_info}_"
        f"Page{current_page}.json"
    )
    folder_path = os.path.join('Properties_Info', 'json_outputs')

    # Save the list of property_info_dict to a JSON file
    os.makedirs(folder_path, exist_ok=True)

    # Convert ObjectId to string in each dictionary
    for item in property_info_list:
        item.pop('_id', None)

    with open(os.path.join(folder_path, file_name),
              'w', encoding='utf-8') as json_file:
        json.dump(property_info_list, json_file, ensure_ascii=False, indent=4)

    print(f"Property information saved to {file_name}")

    # Move to the next page
    current_page += 1

if args.report:  # Check if the report argument is provided
    # Plot the information using the plot_property_info function
    plot_property_info(df)

client.close()
