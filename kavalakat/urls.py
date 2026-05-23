# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
# from .views import APIRootView, HealthCheckView

# admin.site.site_header = 'Kavalakat Admin'
# admin.site.site_title  = 'Kavalakat'
# admin.site.index_title = 'Administration'

# urlpatterns = [

#     # ── Django Admin ───────────────────────────────────────────────
#     path('admin/', admin.site.urls),

#     # ── Custom CMS Dashboard ───────────────────────────────────────
#     path('dashboard/', include('dashboard.urls')),

#     # ── API Health & Root ──────────────────────────────────────────
#     path('api/',        APIRootView.as_view(),    name='api-root'),
#     path('api/health/', HealthCheckView.as_view(), name='health-check'),

#     # ── JWT Auth ───────────────────────────────────────────────────
#     path('api/auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
#     path('api/auth/token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),

#     # ── App APIs (all under /api/) ─────────────────────────────────
#     path('api/', include([
#         path('', include('pages.urls')),
#         path('', include('about.urls')),
#         path('', include('portfolio.urls')),
#         path('', include('blog.urls')),
#         path('', include('contact.urls')),
#         path('', include('ai_module.urls')),
#     ])),

#     # ── API Documentation ──────────────────────────────────────────
#     path('api/schema/',          SpectacularAPIView.as_view(),       name='api-schema'),
#     path('api/docs/',            SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
#     path('api/docs/redoc/',      SpectacularRedocView.as_view(url_name='api-schema'),   name='api-redoc'),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# -------------------------------------------------------

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import APIRootView, HealthCheckView

admin.site.site_header = 'Kavalakat Admin'
admin.site.site_title  = 'Kavalakat'
admin.site.index_title = 'Administration'

urlpatterns = [

    # ── Django Admin ───────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Custom CMS Dashboard ───────────────────────────────────────
    path('dashboard/', include('dashboard.urls')),

    # ── API Health & Root ──────────────────────────────────────────
    path('api/',        APIRootView.as_view(),    name='api-root'),
    path('api/health/', HealthCheckView.as_view(), name='health-check'),

    # ── JWT Auth ───────────────────────────────────────────────────
    path('api/auth/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/auth/token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),

    # ── App APIs (all under /api/) ─────────────────────────────────
    path('api/', include([
        path('', include('pages.urls')),
        path('', include('about.urls')),
        path('', include('portfolio.urls')),
        path('', include('blog.urls')),
        path('', include('contact.urls')),
        path('', include('ai_module.urls')),
        path('', include('services.urls')),
    ])),

    # ── API Documentation ──────────────────────────────────────────
    path('api/schema/',     SpectacularAPIView.as_view(),                              name='api-schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='api-schema'),     name='api-docs'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='api-schema'),       name='api-redoc'),

    # ── Media Files ────────────────────────────────────────────────
    # Serve uploaded media in both DEBUG and production.
    # In production, replace this with a CDN / object-storage (S3, Cloudinary)
    # for better performance and persistence across deploys.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Static files are only needed via Django in DEBUG mode;
# Whitenoise handles them automatically in production.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)