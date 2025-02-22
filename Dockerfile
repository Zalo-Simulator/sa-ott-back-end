FROM python:3.9-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a group and user to run the application
RUN groupadd -g 1000 app_group && \
    useradd -m -g app_group --uid 1000 app_user

# Change ownership of the application files
RUN chown -R app_user:app_group /app

# Switch to the new user
USER app_user

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]