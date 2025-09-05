from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("reply/", views.reply, name="chatbot_reply"),
    path("editor/", views.flow_editor, name="chatbot_editor"),
    path('get_start_node/', views.get_start_node, name='get_start_node'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('check-verification/', views.check_verification_status, name='check_verification'),  # Add this
]