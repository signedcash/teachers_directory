import os
import pandas as pd

from functools import reduce
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from core.utils.importer import import_teachers_from_csv, import_teachers_from_csv_and_zip
from .models import Teacher
from .forms import RegisterForm, TeachersImportForm


class IndexView(RedirectView):
    url = reverse_lazy('teachers_directory')


class CustomLoginView(LoginView):
    template_name = 'signin.html'
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True


class CustomRegisterView(CreateView):
    template_name = 'signup.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')


class TeachersDirectoryListView(ListView):
    """
    Renders a list of teachers based on the search query if provided, otherwise all teachers.
    The rendered list is paginated, displaying 8 results per page.
    Returns:
        HttpResponse: A response containing the rendered HTML page.
    """
    model = Teacher
    template_name = 'teachers_directory_list.html'
    context_object_name = 'teachers'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')

        if query:
            queries = query.split()
            query_filters = [
                Q(first_name__istartswith=query) | 
                Q(last_name__istartswith=query) | 
                Q(subjects_taught__name__istartswith=query) 
                for query in queries
            ]
            queryset = queryset.filter(
                reduce(lambda a, b: a & b, query_filters)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        if query:
            context['query'] = query
        context['title'] = 'Teachers Directory'
        return context


class TeachersDirectoryView(TemplateView):
    """
    Renders the teachers directory page with pagination and search functionality.
    Returns:
        Rendered HTML template with the list of teachers and pagination.
    """
    template_name = 'teachers_directory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Teachers Directory'
        context['current_page'] = self.request.GET.get('page', 1)
        return context


class TeacherProfileView(DetailView):
    """
    Displays the teacher profile page with detailed information about the teacher.
    Returns:
        HttpResponse: The HTTP response with the rendered teacher profile page.
    """
    model = Teacher
    template_name = 'teacher_profile.html'
    context_object_name = 'teacher'


class TeachersImportView(LoginRequiredMixin, FormView):
    """
    View for importing teachers from a CSV file and a zip file containing their profile pictures.
    If the request method is POST and the form is valid, the function will import the teachers data and redirect
    to the teachers directory page. Otherwise, it will render the teachers import form.
    If the form is valid and a CSV file is provided, it will be validated and the data will be extracted from it.
    If a zip file is provided, it will be validated and the profile pictures will be extracted from it and linked to the
    corresponding teachers.
    If any errors occur during the validation or import process, they will be displayed to the user.

    Returns:
        If the request method is POST and the form is valid, redirects to the teachers directory page.
        Otherwise, renders the teachers import form.
    """
    template_name = 'teachers_import.html'
    form_class = TeachersImportForm
    success_url = reverse_lazy('teachers_directory')

    def form_valid(self, form):
        zip_file = form.cleaned_data['zip_file']

        df_teachers = pd.read_csv("data_temp.csv")
        # If a zip file is provided, import the data from the CSV file and the zip file.
        if zip_file:
            import_teachers_from_csv_and_zip(df_teachers, zip_file)
        # If no zip file is provided, import the data from the CSV file only.
        else:
            import_teachers_from_csv(df_teachers)

        if os.path.exists("data_temp.csv"):
            os.remove("data_temp.csv")
        # Redirect to the teachers directory page.
        return super().form_valid(form)
    
    def form_invalid(self, form):
        zip_file_errors = form.errors.get('zip_file')
        zip_file = None if zip_file_errors else form.cleaned_data['zip_file']

        df_teachers = pd.read_csv("data_temp.csv")
        # If a zip file is provided, import the data from the CSV file and the zip file.
        if zip_file:
            import_teachers_from_csv_and_zip(df_teachers, zip_file)
        # If no zip file is provided, import the data from the CSV file only.
        else:
            import_teachers_from_csv(df_teachers)
        
        if os.path.exists("data_temp.csv"):
            os.remove("data_temp.csv")

        # Redirect to the teachers directory page.
        return super().form_invalid(form)