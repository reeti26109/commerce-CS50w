from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from annoying.functions import get_object_or_None

from .models import *

import simplejson as json

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
        return HttpResponseRedirect(reverse("active_listings"))
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
    comments= Comment.objects.filter(name=name)
    viewer= request.user.username
    if (product.seller==viewer):
        seller=True
    else:
        seller=False
    if request.method =="POST":
        newbid= int(request.POST.get('bid'))
        if (product.current_bid >= newbid):
            return render(request, "auctions/product.html",{
            "product": product,
            "message": "Bid should be higher than current price!",
            "comments": comments,
            "seller": seller
        })
        else:
            o = Bid()
            o.user=request.user.username
            o.name=product.name
            o.bid=newbid
            o.save()
            f=  Listing.objects.get(name=name)
            f.current_bid=newbid
            f.save()
            product= Listing.objects.get(name=name)
            return render(request, "auctions/product.html",{
            "product": product,
            "message": "Your bid is placed!",
            "comments": comments,
            "seller": seller
        })
    else:
        return render(request, "auctions/product.html",{
            "product": product,
            "comments": comments,
            "seller": seller
        })


@login_required(login_url='/login')
def create_listing(request):
    if request.method=="POST":
        f=Listing()
        f.name= request.POST["name"]
        f.description= request.POST["description"]
        f.category= request.POST["category"]
        f.starting_bid= request.POST["price"]
        f.current_bid= request.POST["price"]
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


@login_required(login_url='/login')
def comment(request, name):
    product= Listing.objects.get(name=name)
    comment= request.POST.get('comment')
    viewer= request.user.username
    if (product.seller==viewer):
        seller=True
    else:
        seller=False
    c= Comment()
    c.user=request.user.username
    c.name=product.name
    c.content=comment
    c.save()
    comments= Comment.objects.filter(name=name)
    return render(request, "auctions/product.html",{
        "product": product,
        "comments": comments,
        "seller": seller
    })

@login_required(login_url='/login')
def Watchlist(request):
    Products=[]
    user=request.user.username
    try:
        obj=ProductList.objects.get(user=user)
    except ProductList.DoesNotExist:
        obj=None
    if(obj is not None):
        jsonDec = json.decoder.JSONDecoder()
        List = jsonDec.decode(obj.products)
        for item in List:
            try:
                product=Listing.objects.get(name=item)
                Products.append(product)
            except Listing.DoesNotExist:
                pass
    if len(Products)==0:
        empty= True
    else:
        empty= False
    return render(request, "auctions/watchlist.html",{
        "products": Products,
        "empty": empty
    })


@login_required(login_url='/login')
def watchlist(request,name):
    user=request.user.username
    try:
        obj=ProductList.objects.get(user=user)
    except ProductList.DoesNotExist:
        obj=None
    if(obj is not None):
        jsonDec = json.decoder.JSONDecoder()
        List = jsonDec.decode(obj.products)
        List.append(name)
        obj.products=json.dumps(List)
        obj.save()
    else:
        p=ProductList()
        p.user=user
        List= []
        List.append(name)
        p.products=json.dumps(List)
        p.save()
    return HttpResponseRedirect(reverse("Watchlist"))


@login_required(login_url='/login')
def closedlisting(request):
    winners= Winner.objects.all()
    empty=False
    if len(winners)==0:
        empty =True
    return render(request,"auctions/closedlisting.html",{
        "winners": winners,
        "empty": empty
    })

@login_required(login_url='/login')
def closebid(request, name):
    winobj = Winner()
    listobj = Listing.objects.get(name=name)
    obj = get_object_or_None(Bid, name=name, bid=listobj.current_bid)
    if not obj:
        message = "Deleting Bid"
        msg_type = "danger"
    else:
        bidobj = Bid.objects.get(name=name,bid=listobj.current_bid)
        winobj.seller = request.user.username
        winobj.winner = bidobj.user
        winobj.winprice = listobj.current_bid
        winobj.name = name
        winobj.save()
        message = "Bid Closed"
        msg_type = "success"
        # removing from Bid
        bidobj.delete()
    # removing from watchlist
    if ProductList.objects.filter(user=winobj.winner):
        ob = ProductList.objects.filter(user=winobj.winner)
        jsonDec = json.decoder.JSONDecoder()
        List = jsonDec.decode(ob.products)
        List.remove(name)
        ob.products=json.dumps(List)
        ob.save()
    # removing from Comment
    if Comment.objects.filter(name=name):
        commentobj = Comment.objects.filter(name=name)
        commentobj.delete()
    # removing from Listing
    listobj.delete()
    # retrieving the new products list after adding and displaying
    # list of products available in WinnerModel
    winners = Winner.objects.all()
    # checking if there are any products
    empty = False
    if len(winners) == 0:
        empty = True
    return render(request, "auctions/closedlisting.html", {
        "winners": winners,
        "empty": empty,
        "message": message,
        "msg_type": msg_type
    })
