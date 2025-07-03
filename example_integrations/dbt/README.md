# dbt Integration Example

This directory contains a basic dbt setup with PostgreSQL for data transformation and lineage tracking.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Build and start the containers:
```bash
docker-compose up -d
```

2. Access the dbt container:
```bash
docker-compose exec dbt bash
```

3. Initialize a new dbt project (if not already done):
```bash
dbt init my_project
```

4. Configure your dbt project:
- Update `profiles.yml` in the profiles directory
- Modify `dbt_project.yml` as needed

5. Run dbt commands:
```bash
cd my_project
dbt debug    # Test your connection
dbt run      # Run your models
dbt test     # Run your tests
```

## Project Structure

```
.
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Service orchestration
├── requirements.txt     # Python dependencies
└── profiles/           # dbt connection profiles
```

## Environment Variables

The following environment variables are set in the docker-compose.yml:

- `DBT_PROFILES_DIR`: Location of the dbt profiles directory
- Database credentials (for PostgreSQL):
  - User: dbt
  - Password: dbt
  - Database: dbt
  - Port: 5432

## Notes

- The PostgreSQL data is persisted using a Docker volume
- The dbt service exposes port 8080 for potential web interfaces
- All dbt commands should be run from within the dbt container 