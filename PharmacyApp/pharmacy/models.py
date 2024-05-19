from django.db import models
from django.contrib.auth.models import AbstractUser
from tzlocal import get_localzone_name
import re
import logging
import django.forms
from django.urls import reverse
from django.utils import timezone
from datetime import time

logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

class User(AbstractUser):
    status = (
        ("client","client"),
        ("staff","staff")
    )
    status = models.CharField(choices=status, default="client", max_length=6)
    age = models.PositiveSmallIntegerField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    timezone = get_localzone_name()
    groups = None
    user_permissions = None

    
    def save(self, *args, **kwargs):
        phone_pattern = re.compile(r'\+375\((29|33|44|25)\)\d{7}')
        if not re.fullmatch(phone_pattern, str(self.phone)) or self.age < 18 or self.age > 100:

            logging.exception(f"ValidationError, {self.phone} is in incorrect format OR 18 < {self.age} < 100")

            raise django.forms.ValidationError("Error while creating user (Check phone number and age!)")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name
        
class Categories(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Supplier(models.Model): 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    medicines = models.ManyToManyField('Medicines', related_name="supplier", through='Supply')

    def save(self, *args, **kwargs):
        phone_pattern = re.compile(r'\+375\((29|33|44|25)\)\d{7}')
        if not re.fullmatch(phone_pattern, str(self.phone)):

            logging.exception(f"ValidationError, {self.phone} is in incorrect format OR 18 < {self.age} < 100")

            raise django.forms.ValidationError("Error (Check phone number!)")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Supply(models.Model):
    supplier = models.ForeignKey(Supplier, related_name="supply", on_delete=models.CASCADE)
    medicine = models.ForeignKey('Medicines', related_name="supply", on_delete=models.CASCADE)
    
class Medicines(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=9)
    instructions = models.TextField()
    description = models.TextField()
    cost = models.PositiveIntegerField(default=1)
    photo = models.ImageField(upload_to='images/')

    categories = models.ForeignKey(Categories, related_name="medicines", on_delete=models.CASCADE)
    suppliers = models.ForeignKey(Supplier, related_name="suppliers", on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('medicine_detail', kwargs={'pk': self.pk}) 
       
    def __str__(self):
        return self.name
    
class Department(models.Model):
    no = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    open = models.TimeField(default='10:51:24.543425')
    close = models.TimeField(default='10:51:24.543425')

    def __str__(self):
        return self.no    
    
class DepartmentMedicine(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.medicine.name} - {self.department.no} ({self.quantity})"

class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='sale', on_delete=models.CASCADE)
    promocode = models.ForeignKey("Promocode", related_name='sale', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, related_name="sale", on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicines, related_name="items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    price_prom = models.FloatField()
    is_canceled = models.BooleanField(default=False)

    def use_discount(self, promocode):
        if UsedDiscounts.objects.filter(promocode_id=promocode, user_id=self.user).exists():
            return
        self.price_prom *= (100 - promocode.discount) / 100
        self.save()

        UsedDiscounts.objects.create(promocode=promocode, user=self.user)

    def subtotal(self):
        subtotal = self.quantity * self.medicine.cost
        return subtotal

    
class Promocode(models.Model):
    code = models.CharField(max_length=10)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

class UsedDiscounts(models.Model):
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class News(models.Model):
    title = models.TextField(max_length=120)
    content = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)


class CompanyInfo(models.Model):
    text = models.TextField()
    logo = models.ImageField(upload_to='images/')


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date = models.DateField(auto_now_add=True)


class Contact(models.Model):
    description = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images/')



class Vacancy(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    need = models.TextField()


class Review(models.Model):
    title = models.CharField(max_length=100)
    rating = models.IntegerField()
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
