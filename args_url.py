import argparse


def create_parser():
    try:
        parser = argparse.ArgumentParser(
            prog='main.py',
            description='Scrape Switzerland Real Estate Data from https://www.homegate.ch/'
        )

        parser.add_argument("-t", "--type", type=str, choices=['buy', 'rent'],
                            help="Advertisement type", required=True)
        parser.add_argument("-c", "--cities", type=str, nargs="+",
                            help="List of city names. At least one city is required.",
                            required=True)
        parser.add_argument("-rf", "--rooms_from",
                            help="Optional: Minimum Number of Rooms (from)")
        parser.add_argument("-rt", "--rooms_to",
                            help="Optional: Maximum Number of Rooms (to)")
        parser.add_argument("-yf", "--year_from",
                            help="Optional: Year built from")
        parser.add_argument("-yt", "--year_to",
                            help="Optional: Year built to")
        parser.add_argument("-pf", "--price_from",
                            help="Optional: Minimum price")
        parser.add_argument("-pt", "--price_to",
                            help="Optional: Maximum price")
        parser.add_argument("-sf", "--space_from",
                            help="Optional: Minimum Living Space")
        parser.add_argument("-st", "--space_to",
                            help="Optional: Maximum Living Space")
        # If price is not specificly in list, it consider the closer value

        # Add report argument to show relevant plots
        parser.add_argument("-r", "--report", action="store_true",
                            help="Print plots")

        args = parser.parse_args()

        return args
    except Exception as e:
        print(f"Error in creating parser: {e}")


def create_url(base_url):
    args = create_parser()
    # Build the base URL with required arguments
    url = base_url.format(ad_type=args.type, city=args.cities[0])

    # Add optional arguments to the URL if provided
    # If multiple cities are provided
    if len(args.cities) == 2:
        # If two cities provided
        url += "loc=geo-city-{}".format(args.cities[1])
    elif len(args.cities) > 2:
        # If more than two cities provided, append 'loc' parameter
        loc_param = "%2C".join([f"geo-city-{city}" for city in args.cities[1:]])
        url += "loc=geo-city-{}%2C{}".format(args.cities[1], loc_param)

    if args.rooms_from:
        url += "&ac={}".format(args.rooms_from)

    if args.rooms_to:
        url += "&ad={}".format(args.rooms_to)

    if args.price_from:
        if args.type == 'rent':
            url += "&ag={}".format(args.price_from)
        elif args.type == 'buy':
            url += "&ai={}".format(args.price_from)

    if args.price_to:
        if args.type == 'rent':
            url += "&ah={}".format(args.price_to)
        elif args.type == 'buy':
            url += "&aj={}".format(args.price_to)

    if args.year_from:
        url += "&bf={}".format(args.year_from)

    if args.year_to:
        url += "&bg={}".format(args.year_to)

    if args.space_from:
        url += "&ak={}".format(args.space_from)

    if args.space_to:
        url += "&al={}".format(args.space_to)

    return url
