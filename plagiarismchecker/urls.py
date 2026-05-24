from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from plagiarismchecker.views import admin_dashboard
urlpatterns = [
    path('', views.home, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.filetest, name='upload'),
    path('check-text/', views.test, name='check_text'),
    path('compare/', views.fileCompare, name='compare'),
    path('compare-text/', views.twofiletest1, name='compare_text'),
    path('compare-files/', views.twofilecompare1, name='compare_files'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),

    # Backward-compatible aliases
    path('test/', views.test, name='test'),
    path('filetest/', views.filetest, name='filetest'),
    path('compare-page/', views.fileCompare, name='fileCompare'),
    path('twofiletest/', views.twofiletest1, name='twofiletest1'),
    path('twofilecompare/', views.twofilecompare1, name='twofilecompare1'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
]
