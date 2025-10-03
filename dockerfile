FROM python:3.13-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY prompts/ ./prompts/
COPY .env.example .env

# install the package in development mode
RUN pip install -e .

# create logs directory
RUN mkdir -p logs

# default entrypoint: run or serve based on ENV
ENV ENTRYPOINT_MODE=serve
ENTRYPOINT ["sh", "-c", "if [ \"$ENTRYPOINT_MODE\" = \"serve\" ]; then marketing-project serve; else marketing-project run; fi"]