FROM ghcr.io/dbt-labs/dbt-postgres:1.9.0

RUN pip install uv
RUN git clone https://github.com/dbt-labs/dbt-mcp.git /opt/dbt-mcp \
    && cd /opt/dbt-mcp

COPY project /usr/app

RUN mkdir -p /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

WORKDIR /usr/app

ENTRYPOINT ["sleep", "infinity"]