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
