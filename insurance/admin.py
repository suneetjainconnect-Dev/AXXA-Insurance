from django.contrib import admin
from .models import Customer, Policy, Claim, Document, Notification


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'state')
    search_fields = ('user__username', 'phone', 'city')


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'policy_type', 'customer', 'start_date', 'end_date', 'status')
    list_filter = ('policy_type', 'status', 'start_date', 'end_date')
    search_fields = ('policy_number', 'customer__user__username')
    date_hierarchy = 'start_date'


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'claim_type', 'policy', 'customer', 'status', 'claim_amount', 'submitted_at')
    list_filter = ('claim_type', 'status', 'submitted_at')
    search_fields = ('claim_number', 'policy__policy_number', 'customer__user__username')
    date_hierarchy = 'submitted_at'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'policy', 'claim', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
