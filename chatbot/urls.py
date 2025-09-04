from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth_page, name='auth'),
    path("reply/", views.reply, name="chatbot_reply"),
    path("editor/", views.flow_editor, name="chatbot_editor"),
    path('get_start_node/', views.get_start_node, name='get_start_node'),
    path('', views.auth_page, name='auth'),
    path('chatbot/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]