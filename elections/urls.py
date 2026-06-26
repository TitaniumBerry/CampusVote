
from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.home_view, name="home"),
    path("vote/", views.vote_view, name="vote"),
    path("vote/confirm/", views.vote_confirm_view, name="vote_confirm"),
    path("vote/cast/", views.cast_vote_view, name="cast_vote"),
    path("vote/success/", views.vote_success_view, name="vote_success"),
    path("results/", views.results_view, name="results"),
    
]

 
