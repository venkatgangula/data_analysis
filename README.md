# Data Analysis Workbench

A FastAPI and Streamlit application for exploring CSV and Excel datasets. Upload a dataset to inspect its structure, data quality, missing values, duplicates, descriptive statistics, categorical values, and numeric correlations. Upload multiple datasets to discover possible relationships, join keys, and integration suggestions.

## Features

- Analyze `.csv`, `.xlsx`, and `.xls` files.
- Review row and column counts, data types, unique values, and a data preview.
- Detect missing cells and duplicate rows.
- Calculate numeric and categorical statistics.
- Generate correlations for numeric columns.
- Compare and integrate up to five datasets.
- Use the FastAPI endpoints directly or through the Streamlit workbench.

## Tech Stack

- Python 3.10+
- FastAPI and Uvicorn
- Pandas
- Streamlit
- Plotly

## Project Structure

```text
.
├── backend/
│   ├── analysis.py       # File loading and dataset profiling
│   ├── integration.py    # Dataset relationship and integration logic
│   └── main.py            # FastAPI application
├── frontend/
│   └── app.py             # Streamlit interface
├── sample_data.csv        # Example student dataset
├── sample_activity.csv    # Example activity dataset
└── requirements.txt
```

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the Application

Start the API from the `backend` directory:

```powershell
cd backend
uvicorn main:app --reload --port 8001
```

In a second terminal, from the project root, start Streamlit:

```powershell
streamlit run frontend/app.py
```

Open the URL shown by Streamlit, usually `http://localhost:8501`. The app connects to the API at `http://127.0.0.1:8001` by default.

## API Endpoints

### Health check

```http
GET /health
```

### Analyze one dataset

```bash
curl -X POST "http://127.0.0.1:8001/analyze" \


### Integrate multiple datasets

```bash
curl -X POST "http://127.0.0.1:8001/integrate" \


Interactive API documentation is available at `http://127.0.0.1:8001/docs` while the backend is running.

## Notes

- The integration endpoint accepts between two and five datasets.
- Uploaded files must contain a header row and at least one data row.
- Sample datasets are included for local testing. They are ignored by the repository's `.gitignore` by default, so remove those entries if you want to commit them to GitHub.

## License

This project does not currently specify a license.
