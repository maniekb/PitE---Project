from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    label = models.CharField(max_length=30)
    value = models.CharField(max_length=30)


class Exchange(models.Model):
    label = models.CharField(max_length=30)
    value = models.CharField(max_length=30)


class FavouriteCurrency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class FavouriteExchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
