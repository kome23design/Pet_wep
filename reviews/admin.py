from django.contrib import admin
from .models import Review, ReviewModerationHistory


class ReviewModerationHistoryInline(admin.TabularInline):
    model = ReviewModerationHistory
    extra = 0
    readonly_fields = ('moderator', 'action', 'notes', 'timestamp')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('headline', 'customer', 'pet', 'rating', 'status', 'is_verified_purchase', 'created_at')
    list_filter = ('status', 'rating', 'is_verified_purchase', 'created_at')
    search_fields = ('headline', 'customer__username', 'customer__email', 'pet__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_reviews', 'reject_reviews']
    inlines = [ReviewModerationHistoryInline]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(status='approved')
        for review in queryset:
            ReviewModerationHistory.objects.create(
                review=review,
                moderator=request.user,
                action='approved',
                notes='Batch approved via Django Admin'
            )

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
        for review in queryset:
            ReviewModerationHistory.objects.create(
                review=review,
                moderator=request.user,
                action='rejected',
                notes='Batch rejected via Django Admin'
            )
