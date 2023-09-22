import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` function to make HTTP GET requests
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    
    try:
        # Call the get method of the requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except requests.exceptions.RequestException as e:
        # Handle network or request exceptions
        print("Network exception occurred:", str(e))
        return None
    
    status_code = response.status_code
    print("With status {} ".format(status_code))
    
    if response.status_code == 200:
        # Parse JSON response into a Python dictionary
        json_data = response.json()
        return json_data
    else:
        print("Failed to fetch data. Status code:", status_code)
        return None

# Create a function `get_dealers_from_cf` to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Iterate through the list of dealer dictionaries
        for dealer_dict in json_result:
            # Create a CarDealer object with values from the dealer dictionary
            dealer_obj = CarDealer(
                address=dealer_dict["address"],
                city=dealer_dict["city"],
                full_name=dealer_dict["full_name"],
                id=dealer_dict["id"],
                lat=dealer_dict["lat"],
                long=dealer_dict["long"],
                short_name=dealer_dict["short_name"],
                st=dealer_dict["st"],
                zip=dealer_dict["zip"]
            )
            results.append(dealer_obj)
    print('results', results)
    return results

def get_dealer_by_id(url, dealer_id, **kwargs):
    results = []
    # Define the URL with the dealerId parameter
    url_with_id = f"{url}?dealerId={dealer_id}"
    
    # Call get_request with the updated URL
    json_result = get_request(url_with_id, **kwargs)
    
    if json_result:
        # Iterate through the list of dealer dictionaries
        for dealer_dict in json_result:
            # Create a CarDealer object with values from the dealer dictionary
            dealer_obj = CarDealer(
                address=dealer_dict["address"],
                city=dealer_dict["city"],
                full_name=dealer_dict["full_name"],
                id=dealer_dict["id"],
                lat=dealer_dict["lat"],
                long=dealer_dict["long"],
                short_name=dealer_dict["short_name"],
                st=dealer_dict["st"],
                zip=dealer_dict["zip"]
            )
            results.append(dealer_obj)
    print('results', results)
    return results

def get_dealers_by_state(url, state, **kwargs):
    results = []
    # Define the URL with the state parameter
    url_with_state = f"{url}?state={state}"
    
    # Call get_request with the updated URL
    json_result = get_request(url_with_state, **kwargs)
    
    if json_result:
        # Iterate through the list of dealer dictionaries
        for dealer_dict in json_result:
            # Create a CarDealer object with values from the dealer dictionary
            dealer_obj = CarDealer(
                address=dealer_dict["address"],
                city=dealer_dict["city"],
                full_name=dealer_dict["full_name"],
                id=dealer_dict["id"],
                lat=dealer_dict["lat"],
                long=dealer_dict["long"],
                short_name=dealer_dict["short_name"],
                st=dealer_dict["st"],
                zip=dealer_dict["zip"]
            )
            results.append(dealer_obj)
    print('results', results)
    return results

# Create a function `get_dealers_from_cf` to get dealers from a cloud function
def get_dealers_reviews_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Iterate through the list of dealer dictionaries
        for dealer_dict in json_result:
            # Create a CarDealer object with values from the dealer dictionary
            dealer_obj = CarDealer(
                address=dealer_dict["address"],
                city=dealer_dict["city"],
                full_name=dealer_dict["full_name"],
                id=dealer_dict["id"],
                lat=dealer_dict["lat"],
                long=dealer_dict["long"],
                short_name=dealer_dict["short_name"],
                st=dealer_dict["st"],
                zip=dealer_dict["zip"]
            )
            results.append(dealer_obj)
    print('results', results)
    return results

def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    url_with_id = f"{url}?id={dealer_id}"
    # Make a GET request to retrieve reviews for the specified dealer ID
    json_result = get_request(url_with_id, dealerId=dealer_id)
    print("results", json_result)
    if json_result:
        # Iterate through the list of review dictionaries
        for review_dict in json_result:
            print("review_dict", review_dict)
            print("rev", review_dict["review"])
            # Create a DealerReview object with values from the review dictionary
            review_obj = DealerReview(
                dealership=review_dict["dealership"],
                name=review_dict["name"],
                purchase=review_dict["purchase"],
                review=review_dict["review"],
                purchase_date=review_dict["purchase"],
                id=review_dict["id"]
            )
            results.append(review_obj)
    print(results)
    
    return results

