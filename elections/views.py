from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from .models import Election, Candidate, Vote


def get_active_election():
    return Election.objects.filter(status="active").first()


@login_required
def vote_view(request):
    # voting page
    # blocked if no active election or user has already voted for gensec and prez

    election = get_active_election()

    if election is None:
        return render(request, "elections/no_election.html")
    
    user = request.user

    if user.has_voted_president and user.has_voted_gensec:
        return render(request, "elections/already_voted.html")

    president_candidates = election.candidates.filter(position = "president")
    gensec_candidates = election.candidates.filter(position = "gensec")

    return render(request, "elections/vote.html", {
        "election" : election,
        "president_candidates" : president_candidates,
        "gensec_candidates" : gensec_candidates,
        "has_voted_president" : user.has_voted_president,
        "has_voted_gensec" : user.has_voted_gensec
    })


@login_required
def vote_confirm_view(request):
    # confirmation page
    # only reachable via post from vote view
    if request.method != 'POST':
        return redirect("vote")
    
    election = get_active_election()
    if election is None:
        return redirect("vote")
    
    user = request.user
    president_id = request.POST.get("president")
    gensec_id = request.POST.get("gensec")

    errors = []
    president_candidate = None
    gensec_candidate = None

    if not user.has_voted_president:
        if not president_id:
            errors.append("Please select a President candidate.")
        
        else:
            president_candidate = Candidate.objects.filter(
                id = president_id, election=election, position="president"
            ).first()
            if president_candidate is None:
                errors.append("Invalid president candidate selected.")
            
        
    if not user.has_voted_gensec:
        if not gensec_id:
            errors.append("Please select a GenSec candidate.")
        else:
            gensec_candidate = Candidate.objects.filter(
                id=gensec_id, election=election, position="gensec"
            ).first()
            if gensec_candidate is None:
                errors.append("Invalid GenSec candidate selected.")
    
    if errors:
        for error in errors:
            messages.error(request, error)
        return redirect("vote")
    
    request.session["vote_president_id"] = president_candidate.id if president_candidate else None
    request.session["vote_gensec_id"] = gensec_candidate.id if gensec_candidate else None

    return render(request, "elections/vote_confirm.html", {
        "election" : election,
        "president_candidate": president_candidate,
        "gensec_candidate" : gensec_candidate
    })

@login_required
def cast_vote_view(request):
    # final vote submission and writes to db

    if request.method != "POST":
        return redirect("vote")
    
    election = get_active_election()
    if election is None:
        return redirect("vote")

    user = request.user

    if user.has_voted_president and user.has_voted_gensec:
        return render(request, "elections/already_voted.html")
 
    president_id = request.session.pop("vote_president_id", None)
    gensec_id = request.session.pop("vote_gensec_id", None)
 
    if president_id is None and gensec_id is None:
        messages.error(request, "Session expired. Please select your candidates again.")
        return redirect("vote")

    try:
        with transaction.atomic():
            if president_id and not user.has_voted_president:
                president_candidate = Candidate.objects.get(
                    id=president_id, election=election, position="president"
                )
                Vote.objects.create(
                    voter=user,
                    election=election,
                    candidate=president_candidate,
                    position="president",
                )
                user.has_voted_president = True
 
            if gensec_id and not user.has_voted_gensec:
                gensec_candidate = Candidate.objects.get(
                    id=gensec_id, election=election, position="gensec"
                )
                Vote.objects.create(
                    voter=user,
                    election=election,
                    candidate=gensec_candidate,
                    position="gensec",
                )
                user.has_voted_gensec = True
 
            user.save()
 
    except IntegrityError:
        messages.error(request, "You have already voted for this position.")
        return redirect("vote")
 
    except Candidate.DoesNotExist:
        messages.error(request, "Invalid candidate. Please try again.")
        return redirect("vote")
 
    messages.success(request, "Your vote has been cast successfully!")
    return redirect("vote_success")
    




@login_required
def vote_success_view(request):
    # useless thank you page

    return render(request, "elections/vote_success.html")

@login_required
def results_view(request):
    election = Election.objects.filter(status="published").order_by("-created_at").first()

    if election is None:
        closed = Election.objects.filter(status="closed").first()

        return render(request, "elections/results_pending.html", {"closed" : closed})

    
    results = election.results.select_related("candidate").order_by(
        "candidate__position", "-displayed_vote_count"
    )

    president_results = [r for r in results if r.candidate.position=="president"]
    gensec_results = [r for r in results if r.candidate.position == "gensec"]

    return render(request, "elections/results.html", {
        "election" : election,
        "president_results" : president_results,
        "gensec_results" : gensec_results
    })




 
