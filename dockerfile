FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY . .
RUN mkdir -p templates static
# Make port 8080 available to the world outside this container
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--chdir", "app", "main:app"]