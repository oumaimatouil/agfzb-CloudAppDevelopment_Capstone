from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    return render(request, 'djangoapp/index.html' )

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html' )


# Create a `contact` view to return a static contact page
def contact(request):
     return render(request, 'djangoapp/contact.html' )

# Create a `login_request` view to handle sign in request
# Create a `login_request` view to handle sign in request
def login_request(request):
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
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
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
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)





# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://oumaimatouil-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        dealer_names_list = dealer_names.split()
        print(type(dealer_names_list))
        # Create an empty context dictionary
        for dealer in dealerships:
            print("hi")
            print(dealer.st)
        context = {}
        
        # Add the dealerships list to the context
        context['dealerships'] = dealerships
        print("context, context")
        # Return a list of dealer short name
        #return HttpResponse(dealer_names_list)
        #return render(request, 'djangoapp/index.html', {'dealerships': dealerships})
        #return render(request, 'djangoapp/index.html',  {'dealer_names_list': dealer_names_list})
        # Update the return statement to use render with context
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = 'https://oumaimatouil-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews'
        url_2 = "https://oumaimatouil-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/"
        dealership = get_dealer_by_id(url_2, dealer_id)
        reviews = get_dealer_reviews_from_cf(url, dealer_id=dealer_id)
         # Concat all dealer's short name
        #reviews_list= [review.review for review in reviews]
        #dealerships_list= [review.dealership for review in reviews]
        #sentiment_list = [review.sentiment for review in reviews]
        #result = [(i,j) for i,j in zip(dealerships_list, reviews_list)]
        #result_sentiment = [(i,j) for i,j in zip(result, sentiment_list)]
        #context['reviews']=reviews
        context = {
            "reviews":  reviews, 
            "dealer_id": dealer_id,
            "dealer":dealership[0]
        }
        print(reviews[0])


        return render(request, 'djangoapp/dealer_details.html', context)


        #return HttpResponse(result_sentiment)
       # return render(request, 'djangoapp/dealer_details.html', context)




# Create a `get_dealer_details` view to render the reviews of a dealer

# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# View to submit a new review
def add_review(request, dealer_id):
    # User must be logged in before posting a review
    if request.user.is_authenticated:

        # POST request posts the content in the review submission form to the Cloudant DB using the post_review Cloud Function
        if request.method == "POST":
            form = request.POST
            review = dict()
            review["name"] = f"{request.user.first_name} {request.user.last_name}"
            review["dealership"] = dealer_id
            review["review"] = form["content"]
            review["purchase"] = form.get("purchasecheck")
            if review["purchase"]:
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
            car = CarModel.objects.get(pk=form["car"])
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year
            
            # If the user bought the car, get the purchase date
            if form.get("purchasecheck"):
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
            else: 
                review["purchase_date"] = None

            url = "https://oumaimatouil-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"  # API Cloud Function route
            json_payload = {"review": review}  # Create a JSON payload that contains the review data

            # Performing a POST request with the review
            result = post_request(url, json_payload, dealerId=dealer_id)
            if int(result.status_code) == 200:
                print("Review posted successfully.")

            # After posting the review the user is redirected back to the dealer details page
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

    else:
        # If user isn't logged in, redirect to login page
        print("User must be authenticated before posting a review. Please log in.")
        return redirect("/djangoapp/login")


    