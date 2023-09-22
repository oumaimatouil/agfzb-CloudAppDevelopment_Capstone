from django.db import models
from django.utils.timezone import now
from datetime import datetime  # Remove the second 'datetime' here

# Create your models here.

# Create a Car Make model
class CarMake(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name + " " + self.description

# Create a Car Model model
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    dealer_id = models.IntegerField(null=True)  # Fixed typo here
    name = models.CharField(null=False, max_length=50)
    
    # Define choices for car types
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    SPORT = "Sport"
    COUPE = "Coupe"
    MINIVAN = "Mini"
    VAN = "Van"
    PICKUP = "Pickup"
    TRUCK = "Truck"
    BIKE = "Bike"
    SCOOTER = "Scooter"
    OTHER = "Other"
    
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
        (SPORT, "Sport"),
        (COUPE, "Coupe"),
        (MINIVAN, "Mini"),
        (VAN, "Van"),
        (PICKUP, "Pickup"),
        (TRUCK, "Truck"),
        (BIKE, "Bike"),
        (SCOOTER, "Scooter"),
        (OTHER, "Other"),
    ]

    type = models.CharField(
        null=False,
        max_length=50,
        choices=TYPE_CHOICES,
        default=SEDAN
    )

    YEAR_CHOICES = []
    for r in range(1969, (datetime.now().year + 1)):
        YEAR_CHOICES.append((r, r))

    year = models.IntegerField(
        ('year'), choices=YEAR_CHOICES, default=datetime.now().year)

    def __str__(self):
        return self.name + ", " + str(self.year) + ", " + self.type
        

class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name
