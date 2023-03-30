from functools import reduce
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pandas as pd
from core.forms import ImportForm, LoginForm, RegisterForm
from core.models import Subject, Teacher
from core.utils.csv_file_validator import validate_csv_file
from core.utils.importer import import_teachers_from_csv, import_teachers_from_csv_and_zip
from core.utils.zip_file_validator import validate_zip_file
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404



def index(request):
    """
    Redirects to the teachers directory page.
    """
    return redirect('teachers_directory')


def logout_view(request):
    """
    Logs out the user and redirects to the index page.
    """
    logout(request)
    return redirect('index')


def login_view(request):
    """
    Renders a login form for the user and logs them in if the submitted form data is valid.

    Returns:
        If the request method is POST and the user is successfully authenticated, it 
        redirects the user to the index page. If the request method is POST and the user 
        is not successfully authenticated, it renders the login form with an error.
        If the request method is not POST, it simply renders the login form.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'signin.html', {'form': form})


def register_view(request):
    """
    Displays the registration form and creates a new user account if the form is valid.

    Returns:
        HttpResponse: The HTTP response object containing the rendered registration form or a redirect to the home page.
    """
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'signup.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'signup.html', {'form': form})

        
def teachers_directory_list(request):
    """
    Renders a list of teachers based on the search query if provided, otherwise all teachers.
    The rendered list is paginated, displaying 8 results per page.

    Returns:
        HttpResponse: A response containing the rendered HTML page.
    """
    query = request.GET.get('query')
    if query and query != '':
        # If query parameter is present, get teachers that match the query
        if query and query != '':
            queries = query.split()
            # Create a list of Q objects for each word in the query
            query_filters = [Q(first_name__istartswith=query) | Q(last_name__istartswith=query) | Q(subjects_taught__name__istartswith=query) for query in queries]

            # Combine the Q objects using &
            teachers = Teacher.objects.filter(reduce(lambda a, b: a & b, query_filters)).distinct()
    else:
        # Otherwise, get all teachers
        teachers = Teacher.objects.all()
    # Paginate teachers list with 8 teachers per page
    paginator = Paginator(teachers, 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # Create context object with necessary variables
    context = {'title': 'Teachers Directory',
               'page': page}
    if query:
        # Add query parameter to context if present
        context = context | {'query': query} 
    return render(request, 'teachers_directory_list.html', context)


def teachers_directory(request):
    """
    Renders the teachers directory page with pagination and search functionality.

    Returns:
        Rendered HTML template with the list of teachers and pagination.
    """
    # Retrieve all Teacher objects from the database
    teachers = Teacher.objects.all()

    # Create a Paginator object with 8 teachers per page
    paginator = Paginator(teachers, 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    query = request.GET.get('query')
    context = {'title': 'Teachers Directory', 'page': page}
    
    # Add the search query to the context dictionary if it exists
    if query:
        context = context | {'query': query}

    return render(request, 'teachers_directory.html', context)


@login_required(login_url='login')
def teachers_import(request):
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
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the CSV and zip files from the form.
            csv_file = request.FILES.get('csv_file')
            zip_file = request.FILES.get('zip_file')

            # Dictionary to store any validation errors that occur.
            errors = {}

            # If a CSV file is provided, validate it and extract the data from it.
            if csv_file:
                try:
                    df_teachers = validate_csv_file(csv_file)
                except ValueError as e:
                    # Add the error to the errors dictionary.
                    form.add_error('csv_file', str(e).splitlines())

            # If a zip file is provided, validate it.
            if zip_file:
                try:
                    validate_zip_file(zip_file)
                except ValueError as e:
                    # Add the error to the errors dictionary.
                    form.add_error('zip_file', str(e).splitlines())

            # If there were any validation errors, display them to the user.
            if form.errors:
                return render(request, 'teachers_import.html', {'form': form})
            else:
                # Delete all existing teachers and subjects before importing the new data.
                Teacher.objects.all().delete()
                Subject.objects.all().delete()

                # If a zip file is provided, import the data from the CSV file and the zip file.
                if zip_file:
                    import_teachers_from_csv_and_zip(df_teachers, zip_file)
                # If no zip file is provided, import the data from the CSV file only.
                else:
                    import_teachers_from_csv(df_teachers)

                # Redirect to the teachers directory page.
                return redirect('teachers_directory')
    else:
        # If the request method is GET, render the teachers import form.
        form = ImportForm()

    return render(request, 'teachers_import.html', {'form': form})



def teacher_profile(request, teacher_id):
    """
    Displays the teacher profile page with detailed information about the teacher.

    Args:
        teacher_id (int): The ID of the teacher to display.

    Returns:
        HttpResponse: The HTTP response with the rendered teacher profile page.
    """
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    context = {'title': f"{teacher.first_name} {teacher.last_name}",
               'teacher': teacher}
    return render(request, 'teacher_profile.html', context)
