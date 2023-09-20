from django.urls import path
from .views import CreateProject
urlpatterns = [
    path('', CreateProject.as_view() , name="create_project"),
]