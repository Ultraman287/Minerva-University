import requests
from requests.structures import CaseInsensitiveDict

# global variables for API connection
base_url = "https://api.geoapify.com/v1/geocode/search?"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
GEO_API_KEY = "905ce5b894d74115809ac770a99bec8c"
params = {
    'apiKey':GEO_API_KEY,
}

def geocode(address):
    """
    This function takes in a free text of address and 
    returns a tuple of coordinates (longitude, latitude)
    """
    params['text'] = address
    resp = requests.get(base_url, headers=headers, params=params)
    # handle json output, only get geocode coordinates!
    coordinates = resp.json()['features'][0]['geometry']['coordinates']
    longitude = coordinates[0]
    latitude = coordinates[1]
    return (latitude, longitude)