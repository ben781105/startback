
from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,TokenBlacklistView, TokenObtainPairView
)
1
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('sms.urls')),
    #path('accounts/',include('accounts.urls')),
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
