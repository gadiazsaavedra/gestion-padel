from django.urls import path
from .views_temp import temp_view

app_name = "bar"

urlpatterns = [
    path("", temp_view, name="productos_list"),
    path("temp/", temp_view, name="temp"),
]
