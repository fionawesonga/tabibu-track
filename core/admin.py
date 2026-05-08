from django.contrib import admin
from .models import Patient, Medication, Schedule, DoseRecord




class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 3




class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 1
    show_change_link = True




@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'ward', 'assigned_nurse', 'created_at']
    list_filter = ['ward', 'assigned_nurse']
    search_fields = ['name', 'ward']
    inlines = [MedicationInline]




@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'dosage', 'patient', 'is_active', 'created_at']
    list_filter = ['is_active', 'patient']
    search_fields = ['name', 'patient__name']
    inlines = [ScheduleInline]




@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['medication', 'slot']
    list_filter = ['slot']
    search_fields = ['medication__name', 'medication__patient__name']




@admin.register(DoseRecord)
class DoseRecordAdmin(admin.ModelAdmin):
    list_display = ['schedule', 'date', 'administered_by', 'administered_at']
    list_filter = ['date', 'administered_by']
    search_fields = ['schedule__medication__name']
    readonly_fields = ['administered_at']
