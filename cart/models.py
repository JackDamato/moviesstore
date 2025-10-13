from django.db import models
from django.contrib.auth.models import User

REGION_CHOICES = [
    ('NA', 'North America'),
    ('SA', 'South America'),
    ('EU', 'Europe'),
    ('AS', 'Asia'),
    ('AF', 'Africa'),
    ('OC', 'Oceania'),
    ('ME', 'Middle East'),
    ('CA', 'Central America'),
    ('CAR', 'Caribbean'),
]

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.user.username}"

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)  # string reference avoids circular import
    price = models.IntegerField()
    quantity = models.IntegerField()
    location = models.CharField(max_length=3, choices=REGION_CHOICES)

    def __str__(self):
        return f"{self.id} - {self.movie.name} ({self.get_location_display()})"
