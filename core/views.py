from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Patient, Medication, Schedule, DoseRecord, PatientPriority


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def build_patient_data(patients, today):
    patient_data = []
    for patient in patients:
        med_count = patient.medications.filter(is_active=True).count()
        pending_count = 0
        for med in patient.medications.filter(is_active=True):
            for schedule in med.schedules.all():
                given = DoseRecord.objects.filter(
                    schedule=schedule, date=today
                ).exists()
                if not given:
                    pending_count += 1

        if pending_count >= 3 or med_count >= 4:
            level = 'critical'
        elif pending_count == 2 or med_count == 3:
            level = 'high'
        elif pending_count == 1 or med_count == 2:
            level = 'medium'
        else:
            level = 'low'

        try:
            manual = patient.priority
            if manual.level:
                level = manual.level
            reason = manual.reason
        except PatientPriority.DoesNotExist:
            reason = ''

        patient_data.append({
            'patient': patient,
            'level': level,
            'med_count': med_count,
            'pending_count': pending_count,
            'reason': reason,
        })

    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    patient_data.sort(
        key=lambda x: (
            priority_order.get(x['level'], 4),
            -x['pending_count'],
            -x['med_count']
        )
    )
    return patient_data


@login_required
def dashboard(request):
    today = timezone.localdate()

    if request.user.is_superuser:
        nurses = User.objects.filter(is_superuser=False, is_staff=True)
        all_patients = Patient.objects.all().select_related(
            'assigned_nurse', 'priority'
        ).prefetch_related('medications')
        total_patients = all_patients.count()
        total_nurses = nurses.count()
        total_doses_today = DoseRecord.objects.filter(date=today).count()
        total_medications = Medication.objects.filter(is_active=True).count()
        nurse_data = []
        for nurse in nurses:
            nurse_patients = all_patients.filter(assigned_nurse=nurse)
            nurse_data.append({
                'nurse': nurse,
                'patients': nurse_patients,
                'patient_count': nurse_patients.count(),
            })
        unassigned = all_patients.filter(assigned_nurse=None)
        return render(request, 'core/admin_dashboard.html', {
            'nurse_data': nurse_data,
            'unassigned': unassigned,
            'total_patients': total_patients,
            'total_nurses': total_nurses,
            'total_doses_today': total_doses_today,
            'total_medications': total_medications,
            'today': today,
        })

    else:
        patients = Patient.objects.filter(
            assigned_nurse=request.user
        ).prefetch_related('medications__schedules')

        patient_data = build_patient_data(patients, today)

        critical = [p for p in patient_data if p['level'] == 'critical']
        high     = [p for p in patient_data if p['level'] == 'high']
        medium   = [p for p in patient_data if p['level'] == 'medium']
        low      = [p for p in patient_data if p['level'] == 'low']

        return render(request, 'core/dashboard.html', {
            'patient_data': patient_data,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low,
            'today': today,
        })


@login_required
def all_patients(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    patients = Patient.objects.all().select_related(
        'assigned_nurse', 'priority'
    ).prefetch_related('medications')
    return render(request, 'core/all_patients.html', {
        'patients': patients,
        'today': timezone.localdate()
    })


@login_required
def all_nurses(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    nurses = User.objects.filter(is_superuser=False, is_staff=True)
    nurse_data = []
    for nurse in nurses:
        nurse_data.append({
            'nurse': nurse,
            'patient_count': Patient.objects.filter(assigned_nurse=nurse).count(),
        })
    return render(request, 'core/all_nurses.html', {
        'nurse_data': nurse_data,
        'today': timezone.localdate()
    })


@login_required
def all_medications(request):
    # FIX: removed superuser-only guard — nurses can now access this page
    medications = Medication.objects.filter(
        is_active=True
    ).select_related('patient').prefetch_related('schedules')
    return render(request, 'core/all_medications.html', {
        'medications': medications,
        'today': timezone.localdate()
    })


@login_required
def all_doses(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    doses = DoseRecord.objects.select_related(
        'schedule__medication__patient', 'administered_by'
    ).order_by('-date', '-administered_at')[:100]
    return render(request, 'core/all_doses.html', {
        'doses': doses,
        'today': timezone.localdate()
    })


@login_required
def my_patients(request):
    today = timezone.localdate()
    patients = Patient.objects.filter(
        assigned_nurse=request.user
    ).prefetch_related('medications__schedules')
    patient_data = build_patient_data(patients, today)
    critical = [p for p in patient_data if p['level'] == 'critical']
    high     = [p for p in patient_data if p['level'] == 'high']
    medium   = [p for p in patient_data if p['level'] == 'medium']
    low      = [p for p in patient_data if p['level'] == 'low']
    return render(request, 'core/dashboard.html', {
        'patient_data': patient_data,
        'critical': critical,
        'high': high,
        'medium': medium,
        'low': low,
        'today': today,
    })


@login_required
def my_doses(request):
    # FIX: added 'administered_by' to select_related so the Administered By
    # column in the nurse dose records table does not raise a query error
    doses = DoseRecord.objects.filter(
        administered_by=request.user
    ).select_related(
        'schedule__medication__patient',
        'administered_by'
    ).order_by('-date', '-administered_at')[:50]
    return render(request, 'core/my_doses.html', {
        'doses': doses,
        'today': timezone.localdate()
    })


@login_required
def patient_detail(request, patient_id):
    if request.user.is_superuser:
        patient = get_object_or_404(Patient, id=patient_id)
    else:
        patient = get_object_or_404(
            Patient, id=patient_id, assigned_nurse=request.user
        )
    today = timezone.localdate()
    medications = patient.medications.filter(
        is_active=True
    ).prefetch_related('schedules')
    schedule_data = []
    for med in medications:
        for schedule in med.schedules.all():
            already_given = DoseRecord.objects.filter(
                schedule=schedule, date=today
            ).exists()
            schedule_data.append({
                'schedule': schedule,
                'medication': med,
                'already_given': already_given,
            })
    grouped = {'morning': [], 'afternoon': [], 'evening': []}
    for item in schedule_data:
        grouped[item['schedule'].slot].append(item)
    try:
        priority = patient.priority
    except PatientPriority.DoesNotExist:
        priority = None

    # FIX: pass can_administer so the template knows whether to show
    # the "Mark as given" button (nurses only) or the locked read-only pill
    return render(request, 'core/patient_detail.html', {
        'patient': patient,
        'grouped': grouped,
        'today': today,
        'priority': priority,
        'can_administer': not request.user.is_superuser,
    })


@login_required
def administer_dose(request, schedule_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    # Extra server-side guard: admins cannot administer doses even if
    # they somehow reach this endpoint directly
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot administer doses'}, status=403)

    schedule = get_object_or_404(Schedule, id=schedule_id)
    if schedule.medication.patient.assigned_nurse != request.user:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    today = timezone.localdate()
    dose, created = DoseRecord.objects.get_or_create(
        schedule=schedule, date=today,
        defaults={'administered_by': request.user}
    )
    if created:
        return JsonResponse({
            'status': 'success',
            'message': 'Dose recorded successfully'
        })
    else:
        return JsonResponse({
            'status': 'duplicate',
            'message': 'Already administered today'
        }, status=409)
