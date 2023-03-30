from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from core.views import *

# Define URLs for the app
urlpatterns = [
    path('', index, name='index'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    
    path('teachers/directory', teachers_directory, name='teachers_directory'),
    path('teachers/directory/list', teachers_directory_list, name='teachers_directory_list'),
    path('teachers/import', teachers_import, name='teachers_import'),
    path('teachers/<int:teacher_id>/', teacher_profile, name='teacher_profile'),
]

# Add debug-specific URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
