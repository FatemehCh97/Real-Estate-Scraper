from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import os

# Set up Chrome options
options = Options()
options.headless = True
options.add_argument('--no-sandbox')

# Specify the path to the ChromeDriver executable
chrome_driver_path = "chromedriver_win64/chromedriver.exe"

# Set up the Chrome service with the specified path
service = ChromeService(executable_path=chrome_driver_path)


def get_property_item_info(url):
    # Initialize ad_info dictionary
    ad_info = {}

    # Create a Chrome webdriver instance
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    time.sleep(2)

    # Use BS to Parse
    bsobj = BeautifulSoup(browser.page_source, 'html.parser')

    # Title
    page_title = bsobj.title.text
    if page_title:
        ad_info['Title'] = page_title
    else:
        ad_info['Title'] = None

    # Attributes
    ## Price information
    price_container = bsobj.find('div', class_='SpotlightAttributesPrice_item_iVKUf')

    if price_container:
        price_label = price_container.find('div', class_='SpotlightAttributesPrice_label_QpTYZ').text.strip()
        # price_label = bsobj.select_one('div[data-test="costs"] dl dt').text[:-1]
        price_value_spans = price_container.find("div", class_="SpotlightAttributesPrice_value_TqKGz").find_all('span')

        # Check if the price is given or its on request
        if len(price_value_spans) == 1:
            price = price_value_spans[0].text.strip()
            # print(price)
            ad_info[price_label] = price
        else:
            # Extract and print currency and amount
            currency = price_value_spans[0].text.strip()
            amount = price_value_spans[1].text.strip()
            # print(f"Price: {currency} {amount}")
            ad_info[price_label] = currency + ' ' + amount
            ad_info['Price'] = amount[:-2]

    ## Number of Rooms
    rooms_container = bsobj.find('div', class_='SpotlightAttributesNumberOfRooms_item_I09kX')

    if rooms_container:
        number_of_rooms = rooms_container.find('div', class_='SpotlightAttributesNumberOfRooms_value_TUMrd').text.strip()
        ad_info['Rooms'] = number_of_rooms

    ## Living Space
    living_space_container = bsobj.find('div',
                                        class_='SpotlightAttributesLivingSpace_item_daF4o')

    if living_space_container:
        living_space = living_space_container.find('div',
                                                   class_='SpotlightAttributesLivingSpace_value_OiuVM').text.strip()
        ad_info['Living Space'] = living_space

    # Location
    ## Address
    location_container = bsobj.find('div',
                                    'AddressDetails_addressDetails_wuB1A')

    if location_container:
        location = location_container.find('address').text.strip()
        # location = bsobj.select_one('.AddressDetails_addressDetails_wuB1A address').text.strip()
        ad_info['Address'] = location

        if location_container.find('iframe'):
            # Generate Google Maps link
            lat, lon = bsobj.iframe['src'].split('q=')[1].split('&')[0].split(',')
            google_maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            ad_info['Google Maps Link'] = google_maps_link

    ## Advertise in Location
    PartnerList_loc = bsobj.find("ul", class_="PartnerListAvailability_list_kPTac")

    if PartnerList_loc:
        loc_text_1 = PartnerList_loc.find_all("span")[0].text.strip()
        loc_text_2 = PartnerList_loc.find_all("span")[2].text.strip()

        loc_link_1 = PartnerList_loc.find_all("a", class_="PartnerListWidget_link_Cn_Dj")[0]['href']
        loc_link_2 = PartnerList_loc.find_all("a", class_="PartnerListWidget_link_Cn_Dj")[1]['href']

        # Print the results
        ad_info['Loc Ad 1'] = loc_text_1 + ' => ' + loc_link_1
        ad_info['Loc Ad 2'] = loc_text_2 + ' => ' + loc_link_2
        # print(f"{loc_text_1} => {loc_link_1}")
        # print(f"{loc_text_2} => {loc_link_2}")

    # Costs
    costs_dl = bsobj.find('div', {'data-test': 'costs'}).find('dl')

    if costs_dl:
        costs_dt_tags = costs_dl.find_all('dt')
        costs_dd_tags = costs_dl.find_all('dd')

        for dt, dd in zip(costs_dt_tags, costs_dd_tags):
            ad_info[dt.text.strip()[:-1]] = dd.text.strip()

    # Main Information
    main_info = bsobj.find('div', class_='CoreAttributes_coreAttributes_e2NAm')

    if main_info:
        main_info_dict = {}
        for dt, dd in zip(main_info.find('dl').find_all('dt'), main_info.find('dl').find_all('dd')):
            main_info_dict[dt.text.strip()[:-1]] = dd.text.strip()
            # print(f"{dt.text.strip()} {dd.text.strip()}")

        ad_info['Main Information'] = main_info_dict

    # Features and furnishings
    features_names = [item.p.text.strip() for item in bsobj.select('ul.FeaturesFurnishings_list_S54KV li')]

    ad_info['Features'] = []
    if features_names:
        for item in features_names:
            ad_info['Features'].append(item)

    # Description
    descripion_container = bsobj.find('div', class_='Description_descriptionBody_AYyuy')

    if descripion_container:
        description = descripion_container.text.strip()
        ad_info['Description'] = description

    # Advertiser
    ad_container = bsobj.find('div', class_='ListingDetails_column_Nd5tM')

    if ad_container:
        ad_address = ad_container.find('address').text.strip()
        ad_info['Advertiser'] = ad_address

        ad_agency_link = ad_container.find('a')
        if ad_agency_link:
            ad_info['Advertiser Link'] = 'https://www.homegate.ch' + ad_agency_link['href']
            if ad_agency_link.find('title'):
                ad_info['Advertiser Link Title'] = ad_agency_link['title']

    # Contact
    ## Phone
    contact_person = bsobj.find('p', class_='ListerContactPhone_person_hZLKb')
    contact_phone = bsobj.find('a', class_='HgPhoneButton_hgPhoneLink_hHCgl')

    if contact_person:
        ad_info['Contact Name'] = contact_person.text.strip()
    if contact_phone:
        ad_info['Contact Phone Number'] = contact_phone.text.strip()

    ## Tech References
    contact_tech_ref = bsobj.find('dl', class_='ListingTechReferences_techReferencesList_jlZwL')

    if contact_tech_ref:
        for dt, dd in zip(contact_tech_ref.find_all('dt'), contact_tech_ref.find_all('dtd')):
            key = dt.text.strip()
            value = dd.text.strip()
            ad_info[key] = value

    # Fraud prevention: a few useful tips
    fraud_title = bsobj.find("div", class_="FraudReportWidget_body_iiZwT").find("h3").text.strip()
    fraud_items = bsobj.find('div', class_='FraudReportWidget_message_Ox4pu').find_all('li')

    ad_info[fraud_title] = []
    for item in fraud_items:
        ad_info[fraud_title].append(item.text.strip())

    # Tip & Services
    services_title = bsobj.find("section", class_="DetailPage_serviceBoxes_gwseJ").find("h2").text.strip()
    service_boxes = bsobj.find_all('div', class_='ServiceBoxes_serviceBoxWrapper_dc_xv')

    tips_dict = {}
    for box in service_boxes:
        box_title = box.find('h5', class_='ServiceBox_title_nw3Em').text.strip()
        box_description = box.find('p', class_='ServiceBox_description_QgvnI').text.strip()
        box_link = box.find('a')['href']
        box_link_text = box.find('p', class_='ServiceBox_cta_Hhc1Q').text.strip()

        tips_dict[box_title] = box_description + box_link_text + '=>' + box_link

        # print(f"{box_title}\n{box_description}\n{box_link_text} => {box_link}\n")

    ad_info[services_title] = tips_dict

    # Images
    # img_container = bsobj.find('div',
    # class_='DetailPage_listingImageGalleryWrapper_bHJaJ').find_all('img')
    img_container = bsobj.select('.glide__slide img')

    # Create a folder to save images
    folder_name = f"IMG-{url.split('/')[-1]}"

    folder_path = os.path.join('Properties_Info', 'Images', folder_name)

    os.makedirs(folder_path, exist_ok=True)

    # Download and save images
    if img_container:
        for idx, img_tag in enumerate(img_container):
            img_src = img_tag['src']
            # Send a GET request to download the image
            image_response = requests.get(img_src)

            # Check if the image download was successful
            if image_response.status_code == 200:
                # Save the image
                img_filename = f"{idx + 1}.jpg"
                img_path = os.path.join(folder_path, img_filename)

                with open(img_path, 'wb') as img_file:
                    img_file.write(image_response.content)

                # print(f"Image {idx + 1} downloaded successfully.\
                # Saved to: {img_path}")
            else:
                print(f"Failed to download image {idx + 1}.\
                      Status code: {image_response.status_code}")

    # Close the browser
    browser.quit()

    return ad_info
