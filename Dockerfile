FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client

# Copy the current directory contents into the container at /app
COPY . .

# Run Alembic migrations and start the FastAPI application
CMD ["fastapi", "run", "main.py", "--port", "8000"]
