from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from analysis import load_dataframe, profile_dataframe
from integration import integrate_datasets


app = FastAPI(
    title="Data Analysis API",
    description="Backend for uploading datasets and returning analysis results.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "data-analysis-api"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        df = load_dataframe(contents, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read the file: {exc}",
        ) from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="The dataset has no rows.")

    result = profile_dataframe(df)
    result["filename"] = file.filename
    return result


def _load_upload(file: UploadFile, contents: bytes):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Each file must have a filename.")
    if not contents:
        raise HTTPException(status_code=400, detail=f"{file.filename} is empty.")
    try:
        df = load_dataframe(contents, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read {file.filename}: {exc}",
        ) from exc
    if df.empty:
        raise HTTPException(status_code=400, detail=f"{file.filename} has no rows.")
    return file.filename, df


@app.post("/integrate")
async def integrate(files: list[UploadFile] = File(...)) -> dict:
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Upload at least two CSV or Excel files to integrate.",
        )

    datasets = []
    for file in files:
        contents = await file.read()
        datasets.append(_load_upload(file, contents))

    try:
        return integrate_datasets(datasets)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
