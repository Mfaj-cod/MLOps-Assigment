FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy application files
COPY run.py .
COPY config.yaml .
COPY data.csv .

# run the job when container starts
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]
