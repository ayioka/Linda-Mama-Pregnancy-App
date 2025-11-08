from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from datetime import date
from .models import (
    User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent
)

# -------------------------------
# User Admin
# -------------------------------
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = UserAdmin.fieldsets + (
        ('LindaMama Profile', {
            'fields': (
                'role', 
                'phone_number', 
                'emergency_contact_name', 
                'emergency_contact_phone', 
                'date_of_birth', 
            )
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'

# -------------------------------
# PregnancyProfile Admin
# -------------------------------
class PregnancyProfileAdmin(admin.ModelAdmin):
    list_display = ['mother', 'last_menstrual_period', 'estimated_due_date', 'current_trimester']
    list_filter = ['current_trimester', 'blood_type', 'created_at']
    search_fields = ['mother__username', 'known_allergies', 'pre_existing_conditions']
    readonly_fields = ['estimated_due_date', 'current_trimester', 'created_at']

# -------------------------------
# VitalsRecord Admin
# -------------------------------
class VitalsRecordAdmin(admin.ModelAdmin):
    list_display = ['mother', 'record_date', 'weight_kg', 'blood_pressure_display', 'temperature', 'fetal_heart_rate']
    list_filter = ['record_date', 'created_at']
    search_fields = ['mother__username', 'symptoms', 'notes']
    readonly_fields = ['created_at']

    def blood_pressure_display(self, obj):
        if obj.blood_pressure_systolic and obj.blood_pressure_diastolic:
            return f"{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic}"
        return "N/A"
    blood_pressure_display.short_description = 'Blood Pressure'

# -------------------------------
# Appointment Admin
# -------------------------------
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['mother', 'clinician', 'appointment_type', 'scheduled_date', 'status']
    list_filter = ['appointment_type', 'status', 'scheduled_date']
    search_fields = ['mother__username', 'clinician__username', 'reason', 'location']
    readonly_fields = ['created_at']

# -------------------------------
# Message Admin
# -------------------------------
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'subject', 'is_read', 'is_urgent', 'created_at']
    list_filter = ['is_read', 'is_urgent', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'subject', 'content']
    readonly_fields = ['created_at']

# -------------------------------
# EmergencyAlert Admin
# -------------------------------
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ['mother', 'urgency_level', 'is_responded', 'created_at']
    list_filter = ['urgency_level', 'is_responded', 'created_at']
    search_fields = ['mother__username', 'symptoms', 'response_notes']
    readonly_fields = ['created_at']

# -------------------------------
# EducationalContent Admin
# -------------------------------
class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'trimester_target', 'is_featured', 'is_active', 'created_at']
    list_filter = ['content_type', 'trimester_target', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'summary', 'content', 'tags']
    readonly_fields = ['created_at']
    prepopulated_fields = {'slug': ('title',)}

# -------------------------------
# Register models
# -------------------------------
admin.site.register(User, CustomUserAdmin)
admin.site.register(PregnancyProfile, PregnancyProfileAdmin)
admin.site.register(VitalsRecord, VitalsRecordAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmergencyAlert, EmergencyAlertAdmin)
admin.site.register(EducationalContent, EducationalContentAdmin)
