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
        if obj.responded_at and
