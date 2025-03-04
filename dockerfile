FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
# Make port 8080 available to the world outside this container
EXPOSE 8080
CMD ["python", "main.py"]