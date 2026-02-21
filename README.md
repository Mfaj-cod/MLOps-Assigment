# MLOps Pipeline

This repository contains a simple Python application implementing a reproducible batch pipeline with configuration, logging, metrics, and Docker containerization as described in the MLOps Engineering Internship technical assessment.

## Setup Instructions

```bash
# create a virtual environment (optional but recommended)
python -m venv venv
# activate it (Windows example)
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## Dependencies
- pandas
- numpy
- pyyaml


## Local Execution Instructions

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

Example output printed to stdout (values may vary slightly):

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 38,
  "seed": 42,
  "status": "success"
}
```

Log file `run.log` is generated with step-by-step information.

## Docker Instructions

```bash
# build the Docker image
docker build -t mlops-task .

# run the container (this will execute the job and exit)
docker run --rm mlops-task
```

After running, `metrics.json` and `run.log` will be created inside the container (and copied to your working directory if you mount volumes or inspect the container). The final metrics are printed to the container's stdout.

## Expected Output Structure

`metrics.json` follows the schema:

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 38,
  "seed": 42,
  "status": "success"
}
```

For an error condition the output will look like:
```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}
```
