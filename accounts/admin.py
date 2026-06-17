from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from .models import User, OTPVerification



@admin.action(description="Reset user votes for selected users(allow revotes)")
def reset_user_votes(ModelAdmin, request, queryset):
    from elections.models import Vote

    with transaction.atomic():
        deleted_count, _ = Vote.objects.filter(voter__in=queryset).delete()
        updated_count = queryset.update(has_voted_president= False, has_voted_gensec = False)
    
    ModelAdmin.message_user(
        request,
        f"Reset {updated_count} user(s) - deleted {deleted_count} vote(s). They can vote again"
    )




@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email", "get_full_name", "hostel", "room_number", "is_verified", "has_voted_president", "has_voted_gensec", "is_staff"
    )

    list_filter = ("is_verified", "has_voted_president", "has_voted_gensec", "hostel", "is_staff")

    search_fields = ("email", "first_name", "last_name", "hostel")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("BITS Profile", {
            "fields": ("hostel", "room_number"),
        }),
        ("Voting Status", {
            "fields": ("is_verified", "has_voted_president", "has_voted_gensec"),
        }),
    )

    actions = [reset_user_votes]

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("BITS Profile", {
            "fields": ("email", "first_name", "last_name", "hostel", "room_number"),
        }),
    )

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "is_expired")
    readonly_fields = ("created_at",)
    search_fields = ("user__email",)
 
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True  # Shows a green/red icon instead of True/False
    is_expired.short_description = "Expired?"


