from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db import models

from .models import User, Category, Listing, comment, Bid


def index(request):
    allCategories = Category.objects.all()
    active_Listings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        "listings": active_Listings,
        "categories": allCategories
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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

def createListing(request):
    if request.method=="GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
            title = request.POST['Title']
            description = request.POST['Description']
            price = request.POST['Price']
            imageurl = request.POST['ImageUrl']
            category = request.POST['Category']
            currentUser = request.user

            categoryData = Category.objects.get(categoryName=category)

            bid = Bid(user=currentUser, bid = int(price))
            bid.save()

            newListing = Listing(
                title = title,
                price = bid,
                imageurl = imageurl,
                Category = categoryData,
                Owner = currentUser,
                description = description,
            )
            newListing.save()
            return HttpResponseRedirect(reverse("index"))

def displaycategory(request):
    if request.method=="POST":
        categoryFromForm = request.POST['Category']
        category = Category.objects.get(categoryName=categoryFromForm)
        allCategories = Category.objects.all()
        active_Listings = Listing.objects.filter(isActive=True, Category=category)
        return render(request, "auctions/index.html", {
            "listings": active_Listings,
            "categories": allCategories
    })

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.Owner.username,


    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner
    })

def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.Owner.username,
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "update": True,
        "message": "You have ended the Auction!",
    })

def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })


def addWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def removeWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['newComment']

    newComment = comment(
        author = currentUser,
        listing = listingData,
        message = message
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addBid(request, id):
    newBid = request.POST['newBid']
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.Owner.username
    if int(newBid) > listingData.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Your Bid has been placed!!",
            "updated": True,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isOwner": isOwner,
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Your Bid was NOT placed!!",
            "updated": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isOwner": isOwner,
        })
