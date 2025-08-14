from django.urls import path
from . import views


urlpatterns = [
    path('send-sms/', views.send_sms, name='send_sms'),
    path('register/', views.register_user, name='register_user'),
    path('profile/', views.get_user_profile, name='get_user_profile'),
    path('groups/create/', views.create_group,name='create_group'),
    path('groups/<int:group_id>/update/', views.update_group,name='update_group'),
    path('groups/<int:group_id>/delete/', views.delete_group,name='delete_group'),
    path('groups/<int:group_id>/contacts/add/', views.add_contacts_to_group,name='add_contact_to_group'),
    path('contacts/<int:contact_id>/delete/', views.delete_contact,name='delete_contact'),
    path('groups/',views.get_groups,name='get_groups'),

]