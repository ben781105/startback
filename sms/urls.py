from django.urls import path
from .views import send_sms,register_user,get_user_profile


urlpatterns = [
    path('send-sms/', send_sms, name='send_sms'),
    path('register/', register_user, name='register_user'),
    path('profile/', get_user_profile, name='get_user_profile'),

]