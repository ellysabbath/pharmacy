from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ✅ Add this import
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('tinymce', include('tinymce.urls')),
    path('', include('ores.urls')),

    # ✅ Built-in password reset views


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
