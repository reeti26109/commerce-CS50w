from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import *


# def index(request):
#     return render(request, "auctions/index.html")

def home(request):
    return render(request, "auctions/home.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("active_listings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return render(request, "auctions/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def active_listings(request):
    products = Listing.objects.all()
    if len(products)==0:
        empty= True
    else:
        empty= False
    return render(request,"auctions/activelistings.html",{
        "products": products,
        "empty": empty
    }) 

@login_required(login_url='/login')
def product(request,name):
    product= Listing.objects.get(name=name)
    return render(request, "auctions/product.html",{
        "product": product
    })


@login_required(login_url='/login')
def create_listing(request):
    if request.method=="POST":
        f=Listing()
        f.name= request.POST["name"]
        f.description= request.POST["description"]
        f.category= request.POST["category"]
        f.starting_bid= request.POST["price"]
        f.seller= request.user.username
        if request.POST.get('image_link'):
            f.image_link = request.POST.get('image_link')
        else:
            f.image_link = "https://www.aust-biosearch.com.au/wp-content/themes/titan/images/noimage.gif"

        f.save()
        return HttpResponseRedirect(reverse('active_listings'))
    else:
        return render(request, "auctions/createlisting.html")


@login_required(login_url='/login')
def categories(request):
    return render(request, "auctions/categories.html")

@login_required(login_url='/login')
def category(request, category):
    products= Listing.objects.filter(category=category)
    if len(products)==0:
        empty= True
    else:
        empty= False
    return render(request, "auctions/category.html",{
        "products": products,
        "empty": empty,
        "category": category
    })