"""
omr_demo.py
Simple demo to test OMR sheets using omr_scanner.py functions.
Automatically loads a sheet, scans, grades, and prints the score.
"""

import cv2
from omr_scanner import detect_document_and_warp, analyze_image, grade_results, load_answer_keys, CHOICES
import os

# -------------------------
# Config: Select set and sheet
# -------------------------
SET_NAME = "SetA"   # "SetA" or "SetB"
SHEET_FILENAME = "sheet1.jpg"  # change to the file you want to test

# Project folder paths
BASE_FOLDER = r".\OMR_sheets"
ANSWER_KEYS = {
    "SetA": r".\answer_key_A.json",
    "SetB": r".\answer_key_B.json"
}

# -------------------------
# Load image
# -------------------------
sheet_path = os.path.join(BASE_FOLDER, SET_NAME, SHEET_FILENAME)
img = cv2.imread(sheet_path)
if img is None:
    print("Error: Could not load image:", sheet_path)
    exit(1)

# -------------------------
# Load answer key
# -------------------------
key_path = ANSWER_KEYS[SET_NAME]
answer_keys = load_answer_keys(key_path)

# -------------------------
# Scan and grade
# -------------------------
warp, found = detect_document_and_warp(img)
if not found:
    print("Warning: Document not detected properly, results may be inaccurate.")

# Analyze image
data = analyze_image(warp, {}, choices=CHOICES)

# Grade results
grading = grade_results(data["results"], answer_keys)

# -------------------------
# Print summary
# -------------------------
print("=== OMR Demo Result ===")
print("Set:", SET_NAME)
print("Sheet:", SHEET_FILENAME)
print("Total Score:", grading["total_score"])
print("Subject Scores:", grading["subject_scores"])

# -------------------------
# Save graded image and JSON
# -------------------------
out_prefix = os.path.join(BASE_FOLDER, SET_NAME, SHEET_FILENAME.split('.')[0])
cv2.imwrite(f"{out_prefix}_graded.jpg", data["canvas"])
print("Graded image saved as:", f"{out_prefix}_graded.jpg")
