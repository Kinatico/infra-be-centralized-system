FROM python:3.10

WORKDIR /tmp
ENV PYTHONPATH=.:/usr/local/lib/python3.10
# Setup pip and setuptools
RUN pip3 install --upgrade pip setuptools

# Setup FastAPI, Uvicorn, and other libraries
RUN pip3 install fastapi uvicorn requests boto3

# Copy src to container
COPY ./src ./src

# Provide permisison for main.py
RUN chmod 755 ./src/main.py

# Setup entrypoint đto run FastAPI app
ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]