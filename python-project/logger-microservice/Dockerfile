FROM python:3.11-slim

WORKDIR /app

# Copy both your app and the shared_core so editable install works
COPY logger-microservice/ .                 
COPY ../shared_core ./shared_core

# Install dependencies, including editable shared_core
RUN pip install --no-cache-dir -r requirements.txt

# Command to run app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
