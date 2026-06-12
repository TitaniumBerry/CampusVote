from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def vote_view(request):
    # temp for now, will change later
    return render(request, "elections/vote.html")
 
