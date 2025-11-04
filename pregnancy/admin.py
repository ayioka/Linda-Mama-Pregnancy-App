from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Avg
from datetime import date, timedelta
from .models import User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'full_name', 'role', 'is_active', 'date_joined', 'profile_picture_preview']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'profile_picture_preview']
    actions = ['activate_users', 'deactivate_users']
    
    fieldsets = UserAdmin.fieldsets + (
        ('LindaMama Profile', {
            'fields': (
                'role', 
                'phone_number', 
                'emergency_contact_name', 
                'emergency_contact_phone', 
                'date_of_birth', 
                'profile_picture',
                'profile_picture_preview'
            )
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    
    activate_users.short_description = "Activate selected users"
    deactivate_users.short_description = "Deactivate selected users"

class PregnancyProfileAdmin(admin.ModelAdmin):
    list_display = [
        'mother', 
        'last_menstrual_period', 
        'estimated_due_date', 
        'current_trimester', 
        'weeks_pregnant',
        'days_until_due',
        'created_at'
    ]
    list_filter = ['current_trimester', 'blood_type', 'created_at']
    search_fields = [
        'mother__username', 
        'mother__first_name', 
        'mother__last_name',
        'known_allergies',
        'pre_existing_conditions'
    ]
    readonly_fields = [
        'estimated_due_date', 
        'current_trimester', 
        'weeks_pregnant',
        'days_until_due',
        'created_at',
        'updated_at'
    ]
    date_hierarchy = 'last_menstrual_period'
    
    def weeks_pregnant(self, obj):
        return obj.get_weeks_pregnant()
    weeks_pregnant.short_description = 'Weeks Pregnant'
    
    def days_until_due(self, obj):
        return obj.get_days_until_due()
    days_until_due.short_description = 'Days Until Due'

class VitalsRecordAdmin(admin.ModelAdmin):
    list_display = [
        'mother', 
        'record_date', 
        'weight_kg', 
        'blood_pressure_display', 
        'temperature',
        'fetal_heart_rate',
        'has_symptoms'
    ]
    list_filter = ['record_date', 'created_at']
    search_fields = [
        'mother__username', 
        'mother__first_name', 
        'mother__last_name',
        'symptoms',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'record_date'
    
    def blood_pressure_display(self, obj):
        if obj.blood_pressure_systolic and obj.blood_pressure_diastolic:
            return f"{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic}"
        return "N/A"
    blood_pressure_display.short_description = 'Blood Pressure'
    
    def has_symptoms(self, obj):
        return bool(obj.symptoms)
    has_symptoms.boolean = True
    has_symptoms.short_description = 'Has Symptoms'

class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'mother', 
        'clinician', 
        'appointment_type', 
        'scheduled_date', 
        'status_badge',
        'is_upcoming',
        'duration_minutes'
    ]
    list_filter = ['appointment_type', 'status', 'scheduled_date', 'created_at']
    search_fields = [
        'mother__username', 
        'clinician__username', 
        'reason',
        'location',
        'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def status_badge(self, obj):
        colors = {
            'scheduled': 'blue',
            'confirmed': 'green',
            'completed': 'gray',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'orange')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_upcoming(self, obj):
        return obj.scheduled_date > date.today()
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} appointments were confirmed.')
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} appointments were marked as completed.')
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} appointments were cancelled.')
    
    mark_as_confirmed.short_description = "Mark selected appointments as confirmed"
    mark_as_completed.short_description = "Mark selected appointments as completed"
    mark_as_cancelled.short_description = "Mark selected appointments as cancelled"

class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'sender', 
        'receiver', 
        'subject_preview', 
        'is_read', 
        'is_urgent',
        'created_at_formatted'
    ]
    list_filter = ['is_read', 'is_urgent', 'created_at']
    search_fields = [
        'sender__username', 
        'receiver__username', 
        'subject', 
        'content'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_urgent']
    
    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_preview.short_description = 'Subject'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%b %d, %Y %H:%M")
    created_at_formatted.short_description = 'Sent'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages were marked as read.')
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages were marked as unread.')
    
    def mark_as_urgent(self, request, queryset):
        updated = queryset.update(is_urgent=True)
        self.message_user(request, f'{updated} messages were marked as urgent.')
    
    mark_as_read.short_description = "Mark selected messages as read"
    mark_as_unread.short_description = "Mark selected messages as unread"
    mark_as_urgent.short_description = "Mark selected messages as urgent"

class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = [
        'mother', 
        'urgency_level_badge', 
        'symptoms_preview',
        'is_responded', 
        'response_time',
        'created_at'
    ]
    list_filter = ['urgency_level', 'is_responded', 'created_at']
    search_fields = [
        'mother__username', 
        'mother__first_name', 
        'mother__last_name',
        'symptoms',
        'response_notes'
    ]
    readonly_fields = ['created_at', 'updated_at', 'response_time']
    date_hierarchy = 'created_at'
    actions = ['mark_as_responded', 'mark_as_high_urgency']
    
    def urgency_level_badge(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.urgency_level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_urgency_level_display().upper()
        )
    urgency_level_badge.short_description = 'Urgency Level'
    
    def symptoms_preview(self, obj):
        return obj.symptoms[:50] + '...' if len(obj.symptoms) > 50 else obj.symptoms
    symptoms_preview.short_description = 'Symptoms'
    
    def response_time(self, obj):
        if obj.responded_at and obj.created_at:
            return obj.responded_at - obj.created_at
        return None
    response_time.short_description = 'Response Time'
    
    def mark_as_responded(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_responded=True, responded_at=timezone.now())
        self.message_user(request, f'{updated} alerts were marked as responded.')
    
    def mark_as_high_urgency(self, request, queryset):
        updated = queryset.update(urgency_level='high')
        self.message_user(request, f'{updated} alerts were marked as high urgency.')
    
    mark_as_responded.short_description = "Mark selected alerts as responded"
    mark_as_high_urgency.short_description = "Mark selected alerts as high urgency"

class EducationalContentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'content_type_badge', 
        'trimester_target', 
        'is_featured', 
        'is_active',
        'read_time',
        'created_at'
    ]
    list_filter = ['content_type', 'trimester_target', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'summary', 'content', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['mark_as_featured', 'mark_as_active', 'mark_as_inactive']
    
    def content_type_badge(self, obj):
        colors = {
            'article': 'blue',
            'video': 'red',
            'infographic': 'green',
            'tip': 'orange',
            'guide': 'purple'
        }
        color = colors.get(obj.content_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            color,
            obj.get_content_type_display()
        )
    content_type_badge.short_description = 'Content Type'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} content items were marked as featured.')
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} content items were activated.')
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} content items were deactivated.')
    
    mark_as_featured.short_description = "Mark selected content as featured"
    mark_as_active.short_description = "Activate selected content"
    mark_as_inactive.short_description = "Deactivate selected content"

# Custom Admin Site with Dashboard
class LindaMamaAdminSite(admin.AdminSite):
    site_header = "LindaMama Administration"
    site_title = "LindaMama Admin Portal"
    index_title = "Welcome to LindaMama Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='lindamama_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Statistics for the dashboard
        context = {
            **self.each_context(request),
            'total_users': User.objects.count(),
            'total_mothers': User.objects.filter(role='mother').count(),
            'total_clinicians': User.objects.filter(role='clinician').count(),
            'active_pregnancies': PregnancyProfile.objects.count(),
            'today_appointments': Appointment.objects.filter(
                scheduled_date__date=date.today()
            ).count(),
            'pending_alerts': EmergencyAlert.objects.filter(is_responded=False).count(),
            'recent_messages': Message.objects.filter(created_at__date=date.today()).count(),
            'user_stats': User.objects.aggregate(
                total=Count('id'),
                active=Count('id', filter=models.Q(is_active=True)),
                staff=Count('id', filter=models.Q(is_staff=True))
            ),
            'appointment_stats': Appointment.objects.aggregate(
                total=Count('id'),
                scheduled=Count('id', filter=models.Q(status='scheduled')),
                confirmed=Count('id', filter=models.Q(status='confirmed')),
                completed=Count('id', filter=models.Q(status='completed'))
            )
        }
        return render(request, 'admin/lindamama_dashboard.html', context)

# Register models with custom admin site
lindamama_admin = LindaMamaAdminSite(name='lindamama_admin')

lindamama_admin.register(User, CustomUserAdmin)
lindamama_admin.register(PregnancyProfile, PregnancyProfileAdmin)
lindamama_admin.register(VitalsRecord, VitalsRecordAdmin)
lindamama_admin.register(Appointment, AppointmentAdmin)
lindamama_admin.register(Message, MessageAdmin)
lindamama_admin.register(EmergencyAlert, EmergencyAlertAdmin)
lindamama_admin.register(EducationalContent, EducationalContentAdmin)

# Also register with default admin for backward compatibility
admin.site.register(User, CustomUserAdmin)
admin.site.register(PregnancyProfile, PregnancyProfileAdmin)
admin.site.register(VitalsRecord, VitalsRecordAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmergencyAlert, EmergencyAlertAdmin)
admin.site.register(EducationalContent, EducationalContentAdmin)
