from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('administer/<int:schedule_id>/', views.administer_dose, name='administer_dose'),
    path('patients/', views.all_patients, name='all_patients'),
    path('nurses/', views.all_nurses, name='all_nurses'),
    path('medications/', views.all_medications, name='all_medications'),
    path('doses/', views.all_doses, name='all_doses'),
    path('my-patients/', views.my_patients, name='my_patients'),
    path('my-doses/', views.my_doses, name='my_doses'),
]
