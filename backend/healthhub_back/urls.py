from django.urls import path
from .views.hello_view import HelloList

urlpatterns = [
    path("hello/",HelloList.as_view(),name="hello-list")
]