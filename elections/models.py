from django.db import models
from django.conf import settings

class Election(models.Model):
    # one election active at a time

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),    
        ("active", "Active"),        
        ("closed", "Closed"),        
        ("published", "Published"),  # results published
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    class Meta:
        ordering = ["-created_at"]


class Candidate(models.Model):
    POSITION_CHOICES = [
        ("president", "President"),
        ("gensec", "General Secretary")
    ]

    election = models.ForeignKey(
        Election, 
        on_delete=models.CASCADE,
        related_name="candidates"
    )

    name = models.CharField(max_length=200)

    position = models.CharField(max_length=20, choices=POSITION_CHOICES)

    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.get_position_display()} ({self.election.title})"

    class Meta:
        ordering = ["position", "order", "name"]
        unique_together = [("election", "name", "position")]


class Vote(models.Model):
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="votes"
    )

    election = models.ForeignKey(
        Election,
        on_delete=models.PROTECT,   # never delete a candidate who has votes
        related_name = "votes"
    )

    candidate = models.ForeignKey(
    Candidate,
    on_delete=models.PROTECT,
    related_name="votes"
    )

    position = models.CharField(max_length=20, choices=Candidate.POSITION_CHOICES)

    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("voter", "election", "position")]
    
    def __str__(self):
        return (
            f"{self.voter.email} voted for {self.candidate.name}"
            f"({self.get_position_display()}) in {self.election.title}"
        )


class Result(models.Model):
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="results"
    )

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="result",
    )

    displayed_vote_count = models.PositiveIntegerField(default=0)

    is_winner = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("election", "candidate")]

    def __str__(self):
        return f"{self.candidate.name}: {self.displayed_vote_count} votes"




# Create your models here.
