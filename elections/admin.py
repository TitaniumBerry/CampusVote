from django.contrib import admin
from django.db import transaction
from .models import Election, Candidate, Vote, Result
from django.core.mail import send_mass_mail
from accounts.models import User

# Register your models here.
class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1  # blank row for adding candidate
    fields = ("name", "position", "order")


@admin.action(description="Send result announcement email to all verified voters")
def send_result_emails(modeladmin, request, queryset):
    for election in queryset:
        if election.status != "published":
            modeladmin.message_user(
                request,
                f"'{election.title}' is not published yet — skipped.",
                level="warning",
            )
            continue

        results = election.results.select_related("candidate").order_by(
            "candidate__position", "-displayed_vote_count"
        )

        # Build result summary text
        lines = [f"Results for {election.title}\n"]
        for position_label, pos_key in [("President", "president"), ("General Secretary", "gensec")]:
            lines.append(f"\n{position_label}:")
            for r in results:
                if r.candidate.position == pos_key:
                    winner = " (Winner)" if r.is_winner else ""
                    lines.append(f"  {r.candidate.name} — {r.displayed_vote_count} votes{winner}")

        result_text = "\n".join(lines)

        # Get all verified non-staff voters
        voters = User.objects.filter(is_verified=True, is_staff=False)

        emails = tuple(
            (
                f"CampusVote — {election.title} Results",
                f"Hi {voter.first_name},\n\n{result_text}\n\nThank you for participating.",
                None,  
                [voter.email],
            )
            for voter in voters
        )

        send_mass_mail(emails, fail_silently=False)

        modeladmin.message_user(
            request,
            f"Result emails sent to {voters.count()} voters for '{election.title}'.",
        )




@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "total_votes")
    list_filter = ("status",)
    search_fields = ("title",)
    inlines = [CandidateInline]
    actions = [send_result_emails]
 
    def total_votes(self, obj):
        return obj.votes.count()
    total_votes.short_description = "Total Votes Cast"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "election", "order")
    list_filter = ("position", "election")
    search_fields = ("name",)
    ordering = ("election", "position", "order")


@admin.action(description="Reset votes for the voter(s) of selected rows (allows revote)")
def reset_votes_for_voters(modeladmin, request, queryset):
    
    from accounts.models import User
 
    voter_ids = queryset.values_list("voter_id", flat=True).distinct()
 
    with transaction.atomic():
        deleted_count, _ = Vote.objects.filter(voter_id__in=voter_ids).delete()
        updated_count = User.objects.filter(id__in=voter_ids).update(
            has_voted_president=False, has_voted_gensec=False
        )
 
    modeladmin.message_user(
        request,
        f"Reset {updated_count} voter(s) — deleted {deleted_count} vote(s) total. They can now vote again.",
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate", "position", "election", "voted_at")
    list_filter = ("position", "election")
    search_fields = ("voter__email", "candidate__name")
    readonly_fields = ("voter", "candidate", "election", "position", "voted_at")

    actions = [reset_votes_for_voters]
 
    # admin cant change votes
    def has_add_permission(self, request):
        return True
 
    def has_change_permission(self, request, obj=None):
        return True
 
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("candidate", "election", "displayed_vote_count", "is_winner", "updated_at")
    list_filter = ("election", "is_winner")
    search_fields = ("candidate__name",)



