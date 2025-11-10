# UPI Digital Payments API

FastAPI backend for the UPI Digital Payments Analysis project.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python api.py
```

Or using uvicorn:
```bash
uvicorn api:app --reload --port 8000
```

3. Access API docs: http://localhost:8000/docs

## Endpoints

- `GET /` - API info
- `GET /api/summary` - Summary statistics
- `GET /api/states` - State-wise data
- `GET /api/state/{state_name}` - Specific state details
- `GET /api/types` - Transaction types
- `GET /api/brands` - Brand market share
- `GET /api/forecast` - Forecast data
- `GET /api/export` - Export data (CSV/JSON)
- `GET /api/timeseries` - Time series with filters
