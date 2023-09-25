from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id, post_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.urls import reverse


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


        return render(request, 'djangoapp/dealer_details.html', context)


        #return HttpResponse(result_sentiment)
       # return render(request, 'djangoapp/dealer_details.html', context)




# Create a `get_dealer_details` view to render the reviews of a dealer

# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# View to submit a new review
def add_review1(request, dealer_id):
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

def add_review4(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Extract form data
            form = request.POST
            review = {
                "name": f"{request.user.first_name} {request.user.last_name}",
                "dealership": dealer_id,
                "review": form["content"],
                "purchase": form.get("purchasecheck"),
                "car_make": None,
                "car_model": None,
                "car_year": None,
                "purchase_date": None,
            }

            if review["purchase"]:
                try:
                    car_id = int(form.get("car"))
                    car = CarModel.objects.get(pk=car_id)
                    review["car_make"] = car.make.name
                    review["car_model"] = car.name
                    review["car_year"] = car.year.strftime("%Y")
                except CarModel.DoesNotExist:
                    messages.error(request, "Invalid car selection.")

                try:
                    purchase_date = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y")
                    review["purchase_date"] = purchase_date.isoformat()
                except ValueError:
                    messages.error(request, "Invalid purchase date format. Please use MM/DD/YYYY.")

                url = "https://oumaimatouil-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"  # Replace with your API endpoint
                json_payload = {"review": review}

                try:
                    result = post_request(url, json=json_payload,dealer_id=dealer_id)

                    if result.status_code == 200:
                        messages.success(request, "Review posted successfully.")
                    else:
                        messages.error(request, "Failed to post the review.")
                except requests.exceptions.RequestException as e:
                    messages.error(request, f"Error: {str(e)}")

                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        
        # Handle GET request to populate car options in the form
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        return render(request, "djangoapp/add_review.html", {"cars": cars, "dealer_id": dealer_id})

    else:
        messages.error(request, "User must be authenticated before posting a review. Please log in.")
        return redirect("/djangoapp/login")
def add_review5(request, dealer_id):
    # User must be logged in before posting a review
    if request.user.is_authenticated:
        # GET request renders the page with the form for filling out a review
        if request.method == "GET":
            url = f"https://oumaimatouil-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/?id={dealer_id}"
            # Get dealer details from the API
            context = {
                "cars": CarModel.objects.all(),
                "dealer": get_dealer_by_id(url, dealer_id=dealer_id),
            }
            print("dealersin context", context["dealer"])
            return render(request, 'djangoapp/add_review.html', context)

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
            review["car_make"] = car.make
            review["car_model"] = car.name
            review["car_year"] = car.year
            
            # If the user bought the car, get the purchase date
            if form.get("purchasecheck"):
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
            else: 
                review["purchase_date"] = None

            url = "https://oumaimatouil-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"  # API Cloud Function route
            json_payload = {"review": review}  # Create a JSON payload that contains the review data

            # Performing a POST request with the review
            result = post_request(url, json_payload, dealerId=dealer_id)
            if int(result.status_code) == 200:
                print("Review posted successfully.")

            # After posting the review the user is redirected back to the dealer details page
            return redirect(reverse('djangoapp:add_review', args=[dealer_id]))

    else:
        # If user isn't logged in, redirect to login page
        print("User must be authenticated before posting a review. Please log in.")
        return redirect("/djangoapp/login")

def add_review(request, dealer_id):
    # Check if the user is authenticated
    print(f"Received dealer_id: {dealer_id}")
    print(f"Request URL: {request.get_full_path()}")
    if not request.user.is_authenticated:
        # Redirect to the login page or handle it as needed
        return redirect("/djangoapp/login")

    try:
        dealer_id = int(dealer_id)
    except ValueError:
        # Handle invalid dealer ID (You can customize this error message)
        error_message = "Invalid dealer ID"

    # Print the dealer ID before rendering th
    if request.method == "GET":
        url = f"https://oumaimatouil-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealerships/?id={dealer_id}"
        dealers = get_dealer_by_id(url, dealer_id=dealer_id)
        dealer=dealers[0]
        #cars = CarModel.objects.filter(dealer_id=dealer_id)
        cars = CarModel.objects.all()
        print("cars", cars)

        context = {
            "cars": cars,
            "dealer": dealer,  # Include the 'dealer' object in the context
        }
        print("delaer info", context["dealer"].id)
        # Print the dealer ID after it's assigned
        print(f"Dealer ID before rendering: {dealer.id}")
        return render(request, 'djangoapp/add_review.html', context)

    elif request.method == "POST":
        form = request.POST
        print(f"{request.user.first_name} {request.user.last_name}")
        review = {
            "name": f"{request.user.first_name} {request.user.last_name}",
            "dealership": dealer_id,
            "review": form["content"],
            "purchase": form.get("purchasecheck", False),
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
            error_message = "Invalid car ID"

        if form.get("purchasecheck"):
            purchase_date_str = form.get("purchasedate")
            if purchase_date_str:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, "%m/%d/%Y")
                    review["purchase_date"] = purchase_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    # Handle invalid purchase date format (You can customize this error message)
                    error_message = "Invalid purchase date format"

        url = "https://oumaimatouil-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
        json_payload = {"review": review}

        result = post_request(url, json_payload, dealerId=dealer_id)
        if int(result.status_code) == 200:
            print("Review posted successfully.")
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            print(int(result.status_code))
            return redirect("djangoapp:add_review", dealer_id=dealer_id)

    return redirect("/djangoapp/login")