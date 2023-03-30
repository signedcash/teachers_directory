FROM python:3.10.6  

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the required packages
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt --root-user-action=ignore

# Copy the rest of the application files to the container
COPY . .   

# Run the Django migrations
RUN python manage.py migrate  

# Start the Django development server
CMD python manage.py runserver 0.0.0.0:8000  

