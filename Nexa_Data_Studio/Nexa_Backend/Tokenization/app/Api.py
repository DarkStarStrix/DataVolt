"""
Api.py: FastAPI endpoints for dataset generation, progress polling, and download.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from .Core import job_manager
from .Progress import progress_tracker
from .Payment import payment_manager
import io

app = FastAPI()

@app.post("/generate-dataset")
async def generate_dataset(request: Request):
    user_input = await request.json()
    job_id, error = job_manager.start_job(user_input)
    if error:
        return JSONResponse({"error": error}, status_code=400)
    return {"job_id": job_id}

@app.get("/progress/{job_id}")
def get_progress(job_id: str):
    progress = progress_tracker.get(job_id)
    if not progress:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return progress

@app.get("/download/{job_id}")
def download(job_id: str):
    job = job_manager.get_job_status(job_id)
    if not job or job.get("status") != "complete":
        return JSONResponse({"error": "Job not complete"}, status_code=400)
    # Payment check
    plan = job.get("plan", "free")
    tokens = job.get("token_budget", 0)
    if payment_manager.requires_payment(plan, tokens):
        return JSONResponse({"error": "Payment required", "checkout_url": payment_manager.create_checkout_session(plan, job_id)}, status_code=402)
    # In production, use FileResponse to serve the file
    return {
        "download_url": job["result_path"],
        "stats": job.get("stats", {})
    }

@app.get("/download-corpus/{job_id}")
def download_corpus(job_id: str):
    job = job_manager.get_job_status(job_id)
    if not job or job.get("status") != "complete":
        return JSONResponse({"error": "Job not complete"}, status_code=400)
    if job.get("job_type") != "corpus":
        return JSONResponse({"error": "Not a corpus job"}, status_code=400)
    plan = job.get("plan", "free")
    tokens = job.get("token_budget", 0)
    if payment_manager.requires_payment(plan, tokens):
        return JSONResponse({"error": "Payment required", "checkout_url": payment_manager.create_checkout_session(plan, job_id)}, status_code=402)
    jsonl_lines = job.get("jsonl_lines", [])
    stats = job.get("stats", {})
    # Stream the JSONL as a file
    file_like = io.StringIO("\n".join(jsonl_lines))
    headers = {
        "Content-Disposition": f"attachment; filename=scientific_corpus_{job_id}.jsonl"
    }
    return StreamingResponse(file_like, media_type="application/jsonl", headers=headers)

@app.get("/job-stats/{job_id}")
def job_stats(job_id: str):
    job = job_manager.get_job_status(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return {"stats": job.get("stats", {})}

@app.get("/price/{plan}")
def get_price(plan: str):
    price = payment_manager.get_price(plan)
    return {"plan": plan, "price": price}

