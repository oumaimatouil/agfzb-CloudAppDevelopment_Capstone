"""
Module: reviews

This module provides functions for interacting with an external API to retrieve and post
reviews for car dealerships. It also includes a function to analyze the sentiment of reviews
using IBM Watson Natural Language Understanding.

Functions:
- get_request(url, api_key=False, **kwargs): Make HTTP GET requests to the API.
- post_request(url, json_payload, **kwargs): Make HTTP POST requests to the API.
- get_dealers_from_cf(url, **kwargs): Get a list of dealerships from the function.
- get_dealer_by_id(url, dealer_id, **kwargs): Get a specific dealership by ID from the function.
- get_dealers_by_state(url, state, **kwargs): Get dealerships by state from the cloud function.
- get_dealer_reviews_from_cf(url, dealer_id, **kwargs): Get reviews for a specific dealership
  from the cloud function.
- analyze_review_sentiments(dealerreview): Analyze the sentiment of a review using
  IBM Watson Natural Language Understanding.
Usage:
- Import this module to use its functions for handling dealership reviews and sentiment analysis.
"""
import json
import requests
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from .models import CarDealer, DealerReview

# Create a `get_request` function to make HTTP GET requests
def get_request(url,api_key=False, **kwargs):
    """
    Make an HTTP GET request to the specified URL.

    This function sends an HTTP GET request to the given URL and returns the JSON response
    as a Python dictionary. If an API key is provided, it will be included in the request headers.

    Args:
        url (str): The URL to send the GET request to.
        api_key (str, optional): An API key for authentication (default is False).
        **kwargs: Additional keyword arguments to be passed to the requests library.

    Returns:
        dict or None: A Python dictionary containing the JSON response if the request is successful,
        or None if an error occurs.

    Example:
        # Make a GET request to retrieve data from the URL
        response_data = get_request("https://example.com/api/data")

    Note:
        This function handles network exceptions and returns None in case of an error.
    """
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
        except requests.exceptions.RequestException as request_exception:
            # Handle network or request exceptions
            print("Network exception occurred:", str(request_exception))
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

# Function for making HTTP POST requests
def post_request(url, json_payload, **kwargs):
    """
    Make an HTTP POST request to the specified URL with JSON payload.

    This function sends an HTTP POST request to the given URL with a JSON payload
    and returns the response object. Any additional keyword arguments can be passed
    to the requests library.

    Args:
        url (str): The URL to send the POST request to.
        json_payload (dict): A dictionary containing the JSON payload to include in the request.
        **kwargs: Additional keyword arguments to be passed to the requests library.

    Returns:
        Response: An HTTP response object containing the server's response to the request.
    """
    try:
        response = requests.post(url, params=kwargs, json=json_payload['review'])
        response.raise_for_status()
    except requests.exceptions.RequestException as request_exception:
        print("An error occurred while making POST request:", str(request_exception))
    return response

# Create a function `get_dealers_from_cf` to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    """
    Retrieve a list of dealers from a cloud function using HTTP GET.

    This function sends an HTTP GET request to the specified URL to retrieve a list of dealer data
    from a cloud function. It then processes the JSON response and creates CarDealer objects
    for each dealer in the list, storing them in a results list.

    Args:
        url (str): The URL of the cloud function endpoint.
        **kwargs: Additional keyword arguments to be passed to the `get_request` function.

    Returns:
        list: A list of CarDealer objects representing the dealers retrieved from the function.

    Note:
        This function relies on the `get_request` function to make the HTTP GET request.
    """

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
    return results

def get_dealer_by_id(url, dealer_id, **kwargs):
    """
    Retrieve a dealer by ID from a cloud function using HTTP GET.

    This function sends an HTTP GET request to the specified URL with the `dealer_id` parameter
    to retrieve details of a dealer with the given ID from a cloud function. It then processes
    the JSON response and creates a CarDealer object representing the retrieved dealer.

    Args:
        url (str): The URL of the cloud function endpoint.
        dealer_id (int): The ID of the dealer to retrieve.
        **kwargs: Additional keyword arguments to be passed to the `get_request` function.

    Returns:
        list: A list containing a single CarDealer object representing the retrieved dealer.

    Note:
        This function relies on the `get_request` function to make the HTTP GET request.

    """
    results = []
    # Define the URL with the dealerId parameter
    url_with_id = f"{url}?id={int(dealer_id)}"
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
    return results

def get_dealers_by_state(url, state, **kwargs):
    """
    Retrieve a list of dealers in a specific state from a cloud function using HTTP GET.

    This function sends an HTTP GET request to the specified URL with the `state` parameter
    to retrieve a list of dealers located in the given state from a cloud function. It then
    processes the JSON response and creates CarDealer objects for each dealer in the list.

    Args:
        url (str): The URL of the cloud function endpoint.
        state (str): The name of the state for which to retrieve dealers.
        **kwargs: Additional keyword arguments to be passed to the `get_request` function.

    Returns:
        list: A list containing CarDealer objects representing the dealers in the specified state.

    Note:
        This function relies on the `get_request` function to make the HTTP GET request.
    """
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
def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    """
    Retrieve a list of dealers in a specific state from a cloud function using HTTP GET.

    This function sends an HTTP GET request to the specified URL with the `state` parameter
    to retrieve a list of dealers located in the given state from a cloud function. It then
    processes the JSON response and creates CarDealer objects for each dealer in the list.

    Args:
        url (str): The URL of the cloud function endpoint.
        state (str): The name of the state for which to retrieve dealers.
        **kwargs: Additional keyword arguments to be passed to the `get_request` function.

    Returns:
        list: A list containing CarDealer objects representing the dealers in the specified state.

    Note:
        This function relies on the `get_request` function to make the HTTP GET request.
    """
    results = []
    url_with_id = f"{url}?id={dealer_id}"
    # Make a GET request to retrieve reviews for the specified dealer ID
    json_result = get_request(url_with_id, dealerId=dealer_id)
    if json_result:
        # Iterate through the list of review dictionaries
        for review_dict in json_result:
            # Create a DealerReview object with values from the review dictionary
            dealership=review_dict["dealership"]
            name=review_dict["name"]
            purchase=review_dict["purchase"]
            review=review_dict["review"]
            purchase_date=review_dict["purchase"]
            try:
                # These values may be missing
                car_make = review_dict["car_make"]
                car_model = review_dict["car_model"]
                car_year = review_dict["car_year"]
                purchase_date = review_dict["purchase_date"]

                # Creating a review object
                review_obj = DealerReview(dealership=dealership, name=name,
                                          purchase=purchase, review=review, car_make=car_make,
                                          car_model=car_model, car_year=car_year,
                                          purchase_date=purchase_date
                                          )

            except KeyError:
                # Creating a review object with some default values
                review_obj = DealerReview(
                    dealership=dealership, id=id, name=name, purchase=purchase, review=review)
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)['sentiment']['document']['label']
            print(f"sentiment: {review_obj.sentiment}")
            results.append(review_obj)
    return results

# Calls the Watson NLU API and analyses the sentiment of a review
def analyze_review_sentiments(dealerreview):
    """
    Analyze the sentiment of a given review using the IBM Watson NLU service.
    This function uses the IBM Watson NLU service to perform sentiment analysis
    on a given review text. It requires an IBM API key and service URL to access the NLU service.

    Args:
        dealerreview (str): The text of the review to be analyzed for sentiment.

    Returns:
        dict: A dictionary containing sentiment analysis results.
        The dictionary typically includes sentiment labels and scores.

    Example:
        sentiment = analyze_review_sentiments("This is a positive review.")
        print(sentiment)

    Note:
        To use this function, you need to have the IBM Watson NLU service set up
        and provide your API key and
        service URL in the function.
    """
    # Define your IBM Watson NLU API key and service URL
    ibm_api_key = 'Zz6gG6Cnxeas-YNOqFvDuznFt1UU-IYcnZyO8ywowoRI'
    ibm_service_url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/d3f3cb64-9a75-4cc2-9426-e4679e8d8981'

    try:
        # Initialize the IBM Watson NLU client
        authenticator = IAMAuthenticator(ibm_api_key)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2022-04-07',
            authenticator=authenticator
        )
        natural_language_understanding.set_service_url(ibm_service_url)

        # Analyze sentiment using the SDK
        response = natural_language_understanding.analyze(
            text=dealerreview,
            features=Features(sentiment=SentimentOptions())
        ).get_result()

        return response

    except Exception as exception:
        print('An error occurred while analyzing sentiments:', str(exception))
        return None
