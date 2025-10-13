from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('map', views.local_popularity_map, name='home.map'),
    path('api/popularity/', views.popularity_api, name='home.api.popularity'),
    path('api/user-purchases/', views.user_purchases_api, name='home.api.user_purchases'),
]