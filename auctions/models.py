from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=60)

    def __str__(self):
        return self.categoryName


class Bid(models.Model):
    bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")

    def __str__(self):
        return(f"{self.bid} placed by {self.user}")

class Listing(models.Model):
    title = models.CharField(max_length=36)
    description = models.CharField(max_length=256)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bidPrice")
    isActive = models.BooleanField(default=True)
    Owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    Category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True ,related_name="category" )
    imageurl = models.CharField(max_length=1000)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
        return self.title

class comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    message = models.CharField(max_length=256)

    def __str__(self):
        return(f"{self.author} comment on {self.listing}")
