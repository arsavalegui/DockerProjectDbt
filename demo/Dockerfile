FROM ghcr.io/dbt-labs/dbt-core:latest

WORKDIR /app  

RUN pip install --no-cache dbt-postgres

COPY . /app

COPY profiles.yml /app


# RUN ["dbt","debug"]

