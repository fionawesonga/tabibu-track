# tabibu-track
Medication tracking PWA for nursing staff
# MedTrack — Hospital Medication Tracking System

> A Django-based medication administration and scheduling system for nursing staff,
> with a full admin overview and a nurse-facing daily workflow interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [User Roles](#user-roles)
- [Pages and Functionality](#pages-and-functionality)
- [Priority System](#priority-system)
- [PWA Support](#pwa-support)
- [Database Models](#database-models)

---

## Overview

MedTrack is a web-based medication tracking and scheduling system built for hospital
environments. It allows administrators to manage nurses, patients, and prescriptions
from a central dashboard, while nurses can view their assigned patients, track daily
medication schedules, and record dose administration — all from a clean,
mobile-friendly interface.

The system enforces strict role separation: administrators have a read-only view of
patient schedules and cannot mark doses as given. Only the nurse assigned to a patient
can administer doses.

---

## Features

### Admin
- Dashboard with live stats — total nurses, patients, active medications, and doses given today
- Bar chart showing patient and medication load per nurse
- Ward distribution panel showing patient spread across wards
- Unassigned patient warnings
- Full patient list with ward, assigned nurse, and medication count
- Nurse roster with patient count and active status
- System-wide dose records (last 100 entries)
- Read-only patient schedule view — cannot mark doses as given

### Nurse
- Priority-sorted patient dashboard (Critical → High → Medium → Low)
- Patient schedule view split into Morning, Afternoon, and Evening slots
- One-tap dose administration with duplicate detection
- Personal dose history with full record table
- Access to the full medications list with dosage and schedule info

### Shared
- Secure login with role detection (Admin / Nurse toggle)
- Automatic patient priority calculation based on medication count and pending doses
- Manual priority override with reason field
- Installable as a PWA — works offline
- Responsive layout for mobile and desktop

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python 3, Django                  |
| API         | Django REST Framework             |
| Frontend    | Vanilla HTML, CSS, JavaScript     |
| Database    | SQLite (development)              |
| Auth        | Django built-in authentication    |
| Offline     | Service Worker + Web App Manifest |
| Font        | Nunito (Google Fonts)             |

---

## Project Structure
tabibu-track/
├── core/
│   ├── migrations/
│   ├── templatetags/
│   ├── templates/
│   │   └── core/
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── admin_dashboard.html
│   │       ├── dashboard.html
│   │       ├── all_patients.html
│   │       ├── all_nurses.html
│   │       ├── all_medications.html
│   │       ├── all_doses.html
│   │       ├── patient_detail.html
│   │       └── my_doses.html
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── medtrack/
│   └── settings.py
├── static/
├── medenv/
├── manage.py
├── db.sqlite3
├── requirements.txt
└── README.md


## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/tabibu-track.git
cd tabibu-track
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv medenv
source medenv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run database migrations**
```bash
python3 manage.py migrate
```

**5. Create an admin account**
```bash
python3 manage.py createsuperuser
```

**6. Create a nurse account**

Log into the Django admin at `/admin/` and create a user with
`is_staff = True` and `is_superuser = False`.
This account will be treated as a nurse by the system.

**7. Start the development server**
```bash
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## User Roles

The system uses Django's built-in `is_superuser` flag to determine role:

| Flag                                      | Role          | Access                                           |
|-------------------------------------------|---------------|--------------------------------------------------|
| `is_superuser = True`                     | Administrator | Full system overview, read-only patient schedules|
| `is_superuser = False`, `is_staff = True` | Nurse         | Assigned patients only, dose administration      |

Role is detected automatically after login — no separate role model is needed.

---

## Pages and Functionality

### `/` — Dashboard
Renders different pages depending on role. Admin sees the full system overview.
Nurse sees their priority-sorted patient list.

### `/patients/` — All Patients *(Admin only)*
A full table of every patient in the system — ward, assigned nurse,
date of birth, and medication count. Each row links to the patient's schedule.

### `/nurses/` — Nursing Staff *(Admin only)*
A card grid of all registered nurses showing patient count and account status.

### `/medications/` — Medications *(Nurse only)*
A table of all active prescriptions — medication name, dosage, patient,
schedule slots, and special instructions.

### `/doses/` — Dose Records *(Admin only)*
The last 100 dose records system-wide. Shows patient, medication, slot,
date and time, and the nurse who administered each dose.

### `/patient/<id>/` — Patient Schedule
Medications grouped into Morning, Afternoon, and Evening columns.
Nurses see a **Mark as given** button. Admins see a locked **Nurse only** pill
and a read-only notice banner at the top of the page.

### `/administer/<id>/` — Administer Dose *(POST, Nurse only)*
Records a dose. Protected at both the UI level (button hidden for admins)
and the server level (returns `403 Forbidden` if an admin hits it directly).
Uses `get_or_create` to prevent duplicate records for the same schedule on the same day.

### `/my-patients/` — My Patients *(Nurse only)*
The nurse's own patient list sorted by priority level.

### `/my-doses/` — My Dose Records *(Nurse only)*
Every dose the logged-in nurse has administered. Six columns: Patient,
Medication, Slot, Date and time, Administered by, and Status.

---

## Priority System

Priority is calculated automatically in `build_patient_data()` based on
active medication count and pending doses for today:

| Level          | Condition                                              |
|----------------|--------------------------------------------------------|
| 🔴 Critical    | 4 or more medications **or** 3 or more pending doses   |
| 🟠 High        | 3 medications **or** 2 pending doses                   |
| 🔵 Medium      | 2 medications **or** 1 pending dose                    |
| 🟢 Low         | 1 medication and all doses given                       |

If a `PatientPriority` record exists, the manual level overrides the automatic
calculation. An optional reason field can be stored alongside the override.

Patients are sorted Critical → High → Medium → Low. Within each level they are
further sorted by pending dose count and medication count, both descending.

---

## PWA Support

MedTrack is installable as a Progressive Web App. The `base.html` template
registers a `serviceworker.js` and links a `manifest.json`, enabling:

- Installation on Android, iOS, and desktop
- Offline access to previously loaded pages
- App-like experience without a browser toolbar

This is particularly useful for nurses on hospital wards where network
connectivity may be intermittent.

---

## Database Models

### `Patient`
Stores name, ward, date of birth, and a foreign key to the assigned nurse (Django `User`).

### `Medication`
Linked to `Patient`. Stores medication name, dosage, special instructions,
and an `is_active` boolean flag.

### `Schedule`
Linked to `Medication`. Stores the time slot (`morning`, `afternoon`, `evening`)
at which the medication should be given.

### `DoseRecord`
Records a single administration event. Linked to `Schedule`. Stores the date,
exact time, and the nurse (`User`) who gave the dose. Duplicates are prevented
via `get_or_create` on `(schedule, date)`.

### `PatientPriority`
Optional one-to-one override for a patient's priority level. Stores the level
(`critical`, `high`, `medium`, `low`) and a free-text reason field.

---

## License

This project was built as part of a hospital management coursework project.
