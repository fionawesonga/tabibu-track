from django.db import models
from django.contrib.auth.models import User




class Patient(models.Model):
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    ward = models.CharField(max_length=100)
    assigned_nurse = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} — Ward {self.ward}"


    class Meta:
        ordering = ['ward', 'name']




class Medication(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} ({self.dosage}) — {self.patient.name}"


    class Meta:
        ordering = ['name']




class Schedule(models.Model):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    EVENING = 'evening'


    SLOT_CHOICES = [
        (MORNING, 'Morning'),
        (AFTERNOON, 'Afternoon'),
        (EVENING, 'Evening'),
    ]


    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES)


    def __str__(self):
        return f"{self.medication.name} — {self.get_slot_display()}"


    class Meta:
        ordering = ['slot']
        unique_together = ('medication', 'slot')




class DoseRecord(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='dose_records'
    )
    administered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='administered_doses'
    )
    date = models.DateField()
    administered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


    def __str__(self):
        return f"{self.schedule} on {self.date} by {self.administered_by}"


    class Meta:
        ordering = ['-date', 'schedule']
        unique_together = ('schedule', 'date')


class PatientPriority(models.Model):
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

    PRIORITY_CHOICES = [
        (CRITICAL, 'Critical'),
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='priority'
    )
    level = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=MEDIUM)
    reason = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name} — {self.get_level_display()}"

    class Meta:
        ordering = ['level']
