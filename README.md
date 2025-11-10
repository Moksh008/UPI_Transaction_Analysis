UPI Digital Payments Analysis

This repository contains starter code for exploratory data analysis (EDA) on UPI datasets.


Requirements
 - Python 3.8+
 - Install packages from `requirements.txt`:

 ```powershell
 pip install -r requirements.txt
 ```

Quick start
1. Backend:
	```powershell
	cd backend
	python -m pip install -r requirements.txt
	uvicorn app:app --reload --port 8000
	```

2. Frontend (example):
	```powershell
	cd frontend
	npm install
	npm start
	```

3. Full dev (run both):
	- Start backend (step 1) then frontend (step 2). The React app expects the backend at `http://127.0.0.1:8000`.

Clerk integration
- Replace Clerk keys in your frontend environment (`.env.local`) and integrate `@clerk/clerk-react` in `src/App.jsx` and `LoginPage.jsx`.

Quick start
1. Ensure your CSV files are under the `data/` folder (already present).
2. Run the EDA script:

```powershell
python src\eda.py
```

What the script does
- Prints shapes, columns, head(3), missing counts and numeric summaries for each CSV in `data/`.
- Attempts to detect date columns and saves a monthly timeseries plot (first numeric column) under `outputs/plots/`.
- Attempts to detect a state/district column and saves a top-10 bar chart for a numeric column (transactions/value) under `outputs/plots/`.

Next steps
- I can add a Jupyter notebook with interactive plots, or scaffold a Streamlit dashboard. Tell me which you'd prefer.
