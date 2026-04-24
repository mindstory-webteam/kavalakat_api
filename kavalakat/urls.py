from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import APIRootView, HealthCheckView

admin.site.site_header  = 'Kavalakat Admin'
admin.site.site_title   = 'Kavalakat'
admin.site.index_title  = 'Administration'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom Dashboard
    path('dashboard/', include('dashboard.urls')),

    # API root & health
    path('api/',         APIRootView.as_view(),   name='api-root'),
    path('api/health/',  HealthCheckView.as_view(), name='health-check'),

    # JWT
    path('api/auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/auth/token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),

    # App APIs
    path('api/', include('pages.urls')),
    path('api/', include('about.urls')),
    path('api/', include('portfolio.urls')),
    path('api/', include('blog.urls')),
    path('api/', include('contact.urls')),
    path('api/', include('ai_module.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
