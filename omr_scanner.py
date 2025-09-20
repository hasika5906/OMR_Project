import cv2
import numpy as np
import json
from PIL import Image

def load_answer_keys(json_path):
    """Load answer keys from a JSON file"""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data  # returns a dict, e.g., {"1": "A", "2": "B", ...}

def grade_omr_image(image_path, answer_key):
    """
    Process a single OMR image and grade it.
    Returns score, answers dict, and annotated image.
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Example bubble detection (modify according to your template)
    # Here, assume we have 100 questions, 4 options each
    answers = {}
    score = 0
    num_questions = 100
    options = ["A", "B", "C", "D"]

    # Split image into 100 regions (dummy logic for demo; adjust to your layout)
    h, w = th.shape
    step_h = h // num_questions

    for q in range(num_questions):
        y1 = q * step_h
        y2 = (q + 1) * step_h
        row = th[y1:y2, :]
        # sum of white pixels in each column section (4 options)
        step_w = w // len(options)
        bubbled = []
        for i in range(len(options)):
            x1 = i * step_w
            x2 = (i + 1) * step_w
            section = row[:, x1:x2]
            filled = cv2.countNonZero(section)
            bubbled.append(filled)
        selected = np.argmax(bubbled)
        answers[str(q + 1)] = options[selected]
        if str(q + 1) in answer_key and answer_key[str(q + 1)] == options[selected]:
            score += 1
        # Draw selection rectangle for visual feedback
        cv2.rectangle(img, (selected * step_w, y1), ((selected + 1) * step_w, y2), (0, 255, 0), 2)

    return {
        "score": score,
        "answers": answers,
        "image": cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # convert to RGB for PIL display in Streamlit
    }

def process_omr_image(image_path, answer_key):
    """Wrapper function for Streamlit app compatibility"""
    return grade_omr_image(image_path, answer_key)
