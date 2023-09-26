"""
Django Views for Car Dealership Application

This module contains Django views for the Car Dealership Application.
These views handle various user interactions, such as rendering web pages,
processing user login and registration, displaying dealer information,
submitting reviews, and more.

Author: Oumaima TOUIl
Date: September 26, 2023
"""
from datetime import datetime
import logging
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CarModel
from .restapis import (
    get_dealers_from_cf,
    get_dealer_reviews_from_cf,
    get_dealer_by_id,
    post_request,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    """
    Render the index page.

    This view renders the main index page of your web application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered HTML.
    """
    return render(request, 'djangoapp/index.html' )

# Create an `about` view to render a static about page
def about(request):
    """
    Render the about page.

    This view renders the 'about' page of your web application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered HTML.
    """
    return render(request, 'djangoapp/about.html' )


# Create a `contact` view to return a static contact page
def contact(request):
    """
    Render the contact page.

    This view renders the 'contact' page of your web application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered HTML.
    """
    return render(request, 'djangoapp/contact.html' )

# Create a `login_request` view to handle sign in request
def login_request(request):
    """
    Handle user login request.

    This view handles user login requests. It checks the provided username and
    password, and if they are valid, it logs the user in and redirects to the
    'index' page. If the credentials are invalid, it returns to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response that may redirect to 'index' or render
            the login page with an error message.
    """
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'onlinecourse/index.html', context)
    else:
        return render(request, 'onlinecourse/index.html', context)

# Create a `logout_request` view to handle sign out request
def custom_logout(request):
    """
    Handle user logout request.

    This view handles user logout requests. It logs out the currently logged-in user
    based on the session ID in the request, prints a log message with the username,
    and then redirects the user back to the 'index' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response that redirects to the 'index' page.
    """
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    """
    Handle user registration request.

    This view handles both GET and POST requests for user registration.
    - For GET requests, it renders the registration page.
    - For POST requests, it processes user registration by creating a new user
      if the provided username does not already exist, then logs in the user
      and redirects to the 'index' page. If the username already exists, it
      displays an error message and stays on the registration page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response that renders the registration page for
        GET requests or redirects to the 'index' page or stays on the registration
        page with an error message for POST requests.
    """
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exists = User.objects.filter(username=username).exists()
        if not user_exists:
            # Create user in auth_user table
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            # Login the user and redirect to index page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            messages.error(request, "Username already exists. Please choose another username.")
    return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    """
    Get a list of dealerships and render the index page.

    This view handles a GET request to fetch a list of dealerships from an external URL
    and then renders the 'index' page with the list of dealerships in the context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response that renders the 'index' page with the list of
        dealerships in the context.
    """
    if request.method == "GET":
        url = (
            "https://oumaimatouil-3000.theiadocker-1-labs-prod-"
            "theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/")

        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Create an empty context dictionary
        context = {}
        # Add the dealerships list to the context
        context['dealerships'] = dealerships
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, dealer_id):
    """
    Get dealer details and render the dealer details page.

    This view handles a GET request to fetch dealer details, including reviews, from external URLs
    based on the provided `dealer_id`. It then renders the 'dealer_details' page with the
    dealer information and reviews in the context.

    Args:
        request (HttpRequest): The HTTP request object.
        dealer_id (int): The ID of the dealer for which details are requested.

    Returns:
        HttpResponse: The HTTP response that renders the 'dealer_details' page with dealer
        information and reviews in the context.
    """
    context = {}
    if request.method == "GET":
        url = (
            'https://oumaimatouil-5000.theiadocker-1-labs-prod-'
            'theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews')
        url_2 = (
            'https://oumaimatouil-3000.theiadocker-1-labs-prod-'
            'theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/')

        dealership = get_dealer_by_id(url_2, dealer_id)
        print("len dealership", len(dealership))
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
        context = {
            "reviews":  reviews, 
            "dealer_id": dealer_id,
            "dealer":dealership[0]
        }
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    """
    Add or retrieve a review for a dealer and render the add review page.

    This view handles both GET and POST requests for adding or retrieving a review for a dealer.
    - For GET requests, it retrieves dealer information and cars for selection
    and renders the 'add_review' page.
    - For POST requests, it processes the review submission, including checking user authentication,
    and posts the review to an external API.
    If successful, it redirects to the 'dealer_details' page; otherwise, it stays on
    the 'add_review' page with an error message.

    Args:
        request (HttpRequest): The HTTP request object.
        dealer_id (int): The ID of the dealer for which the review is being added.

    Returns:
        HttpResponse: The HTTP response that renders the 'add_review' page with dealer information
        and cars for selection for GET requests
        or redirects to the 'dealer_details' page or stays on the 'add_review' page with
        an error message for POST requests.
    """

    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Redirect to the login page or handle it as needed
        return redirect("/djangoapp/login")
    try:
        dealer_id = int(dealer_id)
    except ValueError:
        # Handle invalid dealer ID (You can customize this error message)
        print("Invalid dealer ID")
    # Print the dealer ID before rendering th
    if request.method == "GET":
        url = (
                f"https://oumaimatouil-3000.theiadocker-1-labs-prod-"
                f"theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/?id={dealer_id}")

        dealers = get_dealer_by_id(url, dealer_id=dealer_id)
        dealer=dealers[0]
        cars = CarModel.objects.all()
        context = {
            "cars": cars,
            "dealer": dealer,  # Include the 'dealer' object in the context
        }
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        form = request.POST
        if form.get("purchasecheck", False) is False:
            purchase = False
        else:
            purchase = True
        review = {
            "name": f"{request.user.first_name} {request.user.last_name}",
            "dealership": dealer_id,
            "review": form["content"],
            "purchase": purchase,
            "time": datetime.utcnow().isoformat(),
        }
        try:
            car_id = int(form["car"])
            car = CarModel.objects.get(pk=car_id)
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = str(car.year)
        except (ValueError, CarModel.DoesNotExist):
            # Handle invalid car ID (You can customize this error message)
            print("Invalid car ID")
        if form.get("purchasecheck"):
            purchase_date_str = form.get("purchasedate")
            if purchase_date_str:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, "%m/%d/%Y")
                    review["purchase_date"] = purchase_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    # Handle invalid purchase date format (You can customize this error message)
                    print("Invalid purchase date format")

        url = (
                "https://oumaimatouil-5000.theiadocker-1-labs-prod-"
                "theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review")

        json_payload = {"review": review}
        result = post_request(url, json_payload, dealerId=dealer_id)
        if int(result.status_code) == 201:
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            print(int(result.status_code))
            return redirect("djangoapp:add_review", dealer_id=dealer_id)

    return redirect("/djangoapp/login")
