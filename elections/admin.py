from django.contrib import admin
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


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate", "position", "election", "voted_at")
    list_filter = ("position", "election")
    search_fields = ("voter__email", "candidate__name")
    readonly_fields = ("voter", "candidate", "election", "position", "voted_at")
 
    # admin cant change votes
    def has_add_permission(self, request):
        return False
 
    def has_change_permission(self, request, obj=None):
        return False
 
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("candidate", "election", "displayed_vote_count", "is_winner", "updated_at")
    list_filter = ("election", "is_winner")
    search_fields = ("candidate__name",)


