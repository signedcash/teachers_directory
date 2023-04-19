from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from core.views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    
    path('teachers/directory/', TeachersDirectoryView.as_view(), name='teachers_directory'),
    path('teachers/directory/list/', TeachersDirectoryListView.as_view(), name='teachers_directory_list'),
    path('teachers/import/', TeachersImportView.as_view(), name='teachers_import'),
    path('teachers/<int:pk>/', TeacherProfileView.as_view(), name='teacher_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
