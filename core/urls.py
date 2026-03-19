from django.urls import path
from . import views

urlpatterns = [
    path("", views.gallery_list,   name="gallery-list"),
    path("<uuid:uuid>/",views.gallery_detail, name="gallery-detail"),
    path("image/<int:pk>/", views.image_proxy,    name="image-proxy"),  
]