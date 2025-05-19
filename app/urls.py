
from .import views
from django.urls import path, include

urlpatterns = [
    
    path("test/", views.test, name="test"),
    path("health", views.health, name="health"),
]
