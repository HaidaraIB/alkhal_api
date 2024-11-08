from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=255)
    purchase_price = models.FloatField()
    selling_price = models.FloatField()


class ItemHistory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    old_name = models.CharField(max_length=255)
    new_name = models.CharField(max_length=255)
    old_category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    new_category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    old_selling_price = models.FloatField()
    new_selling_price = models.FloatField()
    old_purchase_price = models.FloatField()
    new_purchase_price = models.FloatField()
    update_date = models.DateTimeField()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField()
    discount = models.FloatField()
    total_price = models.FloatField()
    total_profit = models.FloatField()
    is_sale = models.BooleanField(default=True)
    notes = models.TextField()


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.FloatField()
    purchase_price = models.FloatField()
    selling_price = models.FloatField()
