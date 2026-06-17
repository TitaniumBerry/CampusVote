from django.contrib import admin
from django.db import transaction
from .models import Election, Candidate, Vote, Result

# Register your models here.
class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1  # blank row for adding candidate
    fields = ("name", "position", "order")

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "total_votes")
    list_filter = ("status",)
    search_fields = ("title",)
    inlines = [CandidateInline]
 
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



