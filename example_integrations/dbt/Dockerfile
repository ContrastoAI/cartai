FROM ghcr.io/dbt-labs/dbt-postgres:1.9.0

RUN pip install uv
RUN git clone https://github.com/dbt-labs/dbt-mcp.git /opt/dbt-mcp \
    && cd /opt/dbt-mcp

WORKDIR /usr/app

COPY .env /usr/app/.env

RUN mkdir -p /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

ENTRYPOINT ["uvx", "--env-file", "/usr/app/.env", "dbt-mcp"]