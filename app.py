"""
app.py
FastAPI backend:
- POST /grade : single file upload (image + answer_key_version)
- POST /batch_grade : upload multiple images in a zip or folder (for hackathon demo we accept multiple file fields)
- Returns JSON with per-subject and total scores, stores graded images & JSON in storage/
"""

import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import json
from typing import List
from omr_scanner import detect_document_and_warp, analyze_image, load_answer_keys, grade_results, NUM_QUESTIONS

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)
ANSWER_KEYS_PATH = "answer_keys/example_keys.json"

app = FastAPI(title="Automated OMR Evaluation API")

@app.post("/grade")
async def grade(image: UploadFile = File(...), version: str = Form(...)):
    # save uploaded image
    content = await image.read()
    temp_name = f"{uuid.uuid4().hex}_{image.filename}"
    temp_path = os.path.join(STORAGE_DIR, temp_name)
    with open(temp_path, "wb") as f:
        f.write(content)

    # load answer keys
    keys = load_answer_keys(ANSWER_KEYS_PATH)
    if version == "flat":
        key_for_version = keys
    else:
        key_for_version = keys.get(version, None)
        if key_for_version is None:
            return JSONResponse({"error": f"Version '{version}' not found in answer_keys"}, status_code=400)

    # process image
    import cv2
    img = cv2.imread(temp_path)
    warp, found = detect_document_and_warp(img)
    data = analyze_image(warp, {},)  # analyze_image doesn't need keys to detect selections
    grading = grade_results(data["results"], key_for_version)

    # save graded image and json
    out_id = uuid.uuid4().hex
    graded_img_path = os.path.join(STORAGE_DIR, f"{out_id}_graded.jpg")
    out_json_path = os.path.join(STORAGE_DIR, f"{out_id}_results.json")
    cv2.imwrite(graded_img_path, data["canvas"])
    with open(out_json_path, "w") as f:
        json.dump({"grading": grading}, f, indent=2)

    # Prepare summary: subject-wise scores (0-20)
    resp = {
        "file": image.filename,
        "graded_image": graded_img_path,
        "result_json": out_json_path,
        "subject_scores": grading["subject_scores"],
        "total_score": grading["total_score"],
        "per_question": grading["per_question"]
    }
    return resp

@app.get("/download/{fname}")
def download_file(fname: str):
    path = os.path.join(STORAGE_DIR, fname)
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error": "file not found"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
