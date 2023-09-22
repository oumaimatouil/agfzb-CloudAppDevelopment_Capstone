import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1  # Make sure this import is correct
from ibm_watson.natural_language_understanding_v1 import Features  # Make sure this import is correct
from ibm_watson.natural_language_understanding_v1 import EntitiesOptions
from ibm_watson.natural_language_understanding_v1 import KeywordsOptions



# Create a `get_request` function to make HTTP GET requests
def get_request(url,api_key=False, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    if api_key:
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key)) 
        except:
            print('An error occured while making a get request')
    else:
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
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            print(f"sentiment: {review_obj.sentiment}")
            results.append(review_obj)
    print(results)
    
    return results
# Calls the Watson NLU API and analyses the sentiment of a review
def analyze_review_sentiments(dealerreview):
    # Define your IBM Watson NLU API key and service URL
    ibm_api_key = 'api_key'
    ibm_service_url = 'service_url'

    # Initialize the IBM Watson NLU client
    authenticator = IAMAuthenticator(ibm_api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(ibm_service_url)

    # Define the text to analyze (assuming 'dealerreview' contains the text)
    text_to_analyze = dealerreview

    # Define the NLU features you want to extract
    nlu_features = Features(
        entities=EntitiesOptions(emotion=True, sentiment=True, limit=2),
        keywords=KeywordsOptions(emotion=True, sentiment=True, limit=2)
    )

    # Create a dictionary with the parameters for the get_request function
    params = {
        "text": text_to_analyze,
        "version": '2022-04-07',
        "features": nlu_features,
        "return_analyzed_text": True  # Adjust this as needed
    }

    # Define the URL for your get_request function
    nlu_url = 'service_url'  # Replace with the actual URL

    # Make a call to the get_request function
    try:
        nlu_response = get_request(nlu_url, api_key=ibm_api_key, **params)
        print("hi from here")
        print(nlu_response)
        return nlu_response
    except Exception as e:
        print('An error occurred while analyzing sentiments:', str(e))
        return None
