FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install poetry
RUN pip install poetry

# Configure poetry to create virtualenv in project
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy the UI application
COPY ui.py .

# Expose the port the app runs on
EXPOSE 8501

# Command to run the application
CMD ["poetry", "run", "streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"] 