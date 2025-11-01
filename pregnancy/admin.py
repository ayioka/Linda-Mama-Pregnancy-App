from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PregnancyProfile, VitalsRecord, Appointment, Message, EmergencyAlert, EducationalContent

class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('role', 'phone_number', 'emergency_contact_name', 
                      'emergency_contact_phone', 'date_of_birth', 'profile_picture')
        }),
    )

class PregnancyProfileAdmin(admin.ModelAdmin):
    list_display = ['mother', 'last_menstrual_period', 'estimated_due_date', 'current_trimester', 'get_weeks_pregnant']
    list_filter = ['current_trimester', 'created_at']
    search_fields = ['mother__username', 'mother__first_name', 'mother__last_name']
    readonly_fields = ['estimated_due_date', 'current_trimester']
    
    def get_weeks_pregnant(self, obj):
        return obj.get_weeks_pregnant()
    get_weeks_pregnant.short_description = 'Weeks Pregnant'

class VitalsRecordAdmin(admin.ModelAdmin):
    list_display = ['mother', 'record_date', 'weight_kg', 'blood_pressure_systolic', 'blood_pressure_diastolic']
    list_filter = ['record_date', 'created_at']
    search_fields = ['mother__username', 'mother__first_name', 'mother__last_name']
    date_hierarchy = 'record_date'

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['mother', 'clinician', 'appointment_type', 'scheduled_date', 'status']
    list_filter = ['appointment_type', 'status', 'scheduled_date']
    search_fields = ['mother__username', 'clinician__username', 'reason']
    date_hierarchy = 'scheduled_date'

class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'subject', 'is_read', 'is_urgent', 'created_at']
    list_filter = ['is_read', 'is_urgent', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'subject', 'content']
    date_hierarchy = 'created_at'

class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ['mother', 'urgency_level', 'is_responded', 'created_at']
    list_filter = ['urgency_level', 'is_responded', 'created_at']
    search_fields = ['mother__username', 'symptoms']
    date_hierarchy = 'created_at'

class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'trimester_target', 'is_featured', 'is_active', 'created_at']
    list_filter = ['content_type', 'trimester_target', 'is_featured', 'is_active']
    search_fields = ['title', 'summary', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(PregnancyProfile, PregnancyProfileAdmin)
admin.site.register(VitalsRecord, VitalsRecordAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmergencyAlert, EmergencyAlertAdmin)
admin.site.register(EducationalContent, EducationalContentAdmin)
