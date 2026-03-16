# Weather Data ETL Pipeline with Apache Airflow

A production-ready data pipeline demonstrating modern ETL practices using Apache Airflow, Docker, and PostgreSQL. This project extracts real-time weather data from the Open-Meteo API, transforms it, and loads it into a PostgreSQL database.

## 🎯 Project Overview

This project showcases a complete ETL (Extract-Transform-Load) workflow with:
- **Orchestration**: Apache Airflow for task scheduling and monitoring
- **Data Source**: Open-Meteo weather API (free, no authentication required)
- **Data Processing**: Python-based data transformation
- **Storage**: PostgreSQL database for data persistence
- **Containerization**: Docker for reproducible deployments

## ✨ Key Features

- ✅ **Modular Task Design**: Three independent tasks (extract, transform, load) with automatic dependency management
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Dynamic Scheduling**: Configurable daily runs with catch-up prevention
- ✅ **Data Validation**: Transforms API responses into structured data
- ✅ **Container-Ready**: Full Docker support via Astronomer's Astro Runtime
- ✅ **Development Environment**: Local Airflow UI with Postgres for testing

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | Apache Airflow 2.x |
| Runtime | Astronomer Astro Runtime 3.1 |
| Database | PostgreSQL 13 |
| API | Open-Meteo (Free Weather API) |
| Language | Python 3.12 |
| Containerization | Docker & Docker Compose |

## 📋 Prerequisites

- Docker & Docker Compose
- Astronomer CLI (`pip install astro`)
- Python 3.8+ (for local development)

## 🚀 Getting Started

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/airflow-weather-pipeline.git
cd airflow-weather-pipeline
```

### 2. Start Airflow Locally

```bash
astro dev start
```

This command spins up 5 Docker containers:
- PostgreSQL (database)
- Scheduler (task orchestration)
- DAG Processor (DAG parsing)
- API Server (Airflow UI)
- Triggerer (deferred task support)

### 3. Access Airflow UI

Open your browser to **http://localhost:8080**

Default credentials:
- Username: `admin`
- Password: `admin`

### 4. Configure Database Connection

1. Navigate to **Admin** → **Connections**
2. Click **Create**
3. Fill in the connection details:
   - **Connection ID**: `postgres_default`
   - **Connection Type**: Postgres
   - **Host**: `postgres`
   - **Database**: `postgres`
   - **Login**: `postgres`
   - **Password**: `postgres`
   - **Port**: `5432`

### 5. Trigger the DAG

- Locate **`weather_etl_pipeline`** in the DAG list
- Switch the toggle to **ON** to enable scheduling
- Or click **Trigger DAG** to run immediately

## 📊 Pipeline Architecture

```
Extract Weather Data
        ↓
        └→ API Request (Open-Meteo)
           - Latitude: 51.5074 (London)
           - Longitude: -0.1278
           └→ Returns JSON with current weather

Transform Data
        ↓
        └→ Parse API Response
           - Extract temperature
           - Extract wind speed & direction
           - Extract weather code
           └→ Structured Dictionary

Load to Database
        ↓
        └→ Create/Recreate Table
           └→ Insert Transformed Data
              └→ PostgreSQL Storage
```

## 📁 Project Structure

```
airflow-weather-pipeline/
├── dags/
│   ├── etlweather.py          # Main ETL pipeline DAG
│   └── exampledag.py          # Example reference DAG
├── include/                    # Static files, SQL scripts, etc.
├── plugins/                    # Custom Airflow plugins
├── tests/                      # DAG tests
├── docker-compose.yml         # Local Postgres configuration
├── Dockerfile                 # Astro Runtime image
├── requirements.txt           # Python dependencies
├── packages.txt              # OS-level packages
├── airflow_settings.yaml     # Local Airflow configs
└── README.md                 # This file
```

## 🔍 DAG Overview

### Task 1: `extract_weather_data()`
- Fetches current weather from Open-Meteo API
- Handles API failures with exception raising
- Returns raw JSON data (passed via XCom)

**Output**: JSON with fields: `current_weather`, `current_weather_units`, etc.

### Task 2: `transform_weather_data()`
- Parses JSON data into structured format
- Extracts key metrics:
  - Temperature (°C)
  - Wind Speed (km/h)
  - Wind Direction (degrees)
  - Weather Code (WMO classification)
- Preserves location coordinates (London)

**Output**: Dictionary with 6 weather attributes

### Task 3: `load_weather_data()`
- Connects to PostgreSQL via Airflow Hook
- Drops & recreates `weather_data` table (idempotent)
- Inserts transformed data
- Commits transaction

**Output**: Data persisted in database

## 🧪 Testing Locally

Run the DAG with a test date:

```bash
astro dev bash
airflow dags test weather_etl_pipeline 2024-01-01
```

Check logs in the Airflow UI or:

```bash
astro dev logs --scheduler
astro dev logs --dag-processor
```

## 📊 Database Schema

```sql
CREATE TABLE weather_data (
    latitude FLOAT,
    longitude FLOAT,
    temperature FLOAT,
    windspeed FLOAT,
    winddirection FLOAT,
    weathercode INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

### Schedule
- **Frequency**: Daily (`@daily`)
- **Catchup**: Disabled (no backfill on missed runs)
- **Timezone**: UTC

### Coordinates (Configurable)
```python
LATITUDE = '51.5074'   # London
LONGITUDE = '-0.1278'  # London
```

Change these values in `dags/etlweather.py` to track different locations.

## 🚀 Deployment to Astronomer

1. **Create Astronomer account** at [astronomer.io](https://astronomer.io)

2. **Deploy**:
```bash
astro deployment create
astro deploy
```

3. **Environment Variables** (in Astronomer UI):
```
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

4. Set `postgres_default` connection in Astronomer UI with production database credentials.

## 📚 Learning Outcomes

This project demonstrates:

- ✅ **Apache Airflow**: DAG creation, task dependencies, TaskFlow API
- ✅ **Python**: Decorators, error handling, data structures
- ✅ **APIs**: REST API integration with requests library
- ✅ **Databases**: PostgreSQL connection management, DDL/DML operations
- ✅ **Docker**: Container orchestration with Docker Compose
- ✅ **DevOps**: Local development, logging, monitoring
- ✅ **Software Engineering**: Modular design, idempotency, reproducibility

## 🐛 Troubleshooting

### DAG not appearing in UI
- Check DAG processor logs: `astro dev logs --dag-processor`
- Verify PostgreSQL connection exists
- Ensure no Python syntax errors

### Database connection errors
- Verify `postgres_default` connection in Airflow UI
- Test connection from Admin → Connections
- Check container is running: `docker ps`

### Port conflicts
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services and restart
astro dev stop
astro dev start
```

## 📖 Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Astronomer Getting Started](https://www.astronomer.io/docs/astro/get-started/)
- [Open-Meteo API](https://open-meteo.com/en/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

[Your Name]

---

**Questions?** Feel free to open an issue or reach out!
