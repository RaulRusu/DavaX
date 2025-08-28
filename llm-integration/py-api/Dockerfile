FROM python:3.11-slim

WORKDIR /app

COPY py-api/ .

# Install dependencies, including editable shared_core
RUN pip install --no-cache-dir -r requirements.txt

# Command to run app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
