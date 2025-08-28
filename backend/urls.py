
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView
)
1
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('sms.urls')),
    #path('api/', include('accounts.urls')), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout', TokenBlacklistView.as_view(), name='token_blacklist'),
]
