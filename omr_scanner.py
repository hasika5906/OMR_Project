import os
import cv2
import json
import numpy as np

def load_answer_keys(file_path):
    """Load JSON answer key."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def grade_omr_image(image_path, answer_key):
    """Process single OMR image and return score."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or invalid format.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours (bubbles)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by size (remove noise)
    bubble_contours = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)
        if 15 < w < 50 and 0.8 < aspect_ratio < 1.2:  # adjust these thresholds
            bubble_contours.append(cnt)

    bubble_contours = sorted(bubble_contours, key=lambda c: cv2.boundingRect(c)[1])  # top to bottom

    # Assuming each question has 4 options (A-D)
    questions = len(answer_key)
    score = 0

    for q in range(questions):
        # get 4 bubbles per question
        start = q*4
        if start + 4 > len(bubble_contours):
            continue

        question_bubbles = bubble_contours[start:start+4]
        filled = []

        for idx, cnt in enumerate(question_bubbles):
            mask = np.zeros(th.shape, dtype="uint8")
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            total = cv2.countNonZero(cv2.bitwise_and(th, th, mask=mask))
            filled.append(total)

        # Choose the bubble with max filled pixels
        selected_idx = np.argmax(filled)
        selected_answer = chr(ord('A') + selected_idx)

        # Compare with answer key
        correct_answer = answer_key[str(q+1)]
        if selected_answer == correct_answer:
            score += 1

    return score

def process_omr_folder(folder_path, answer_key_path):
    """Process all images in a folder and grade them."""
    answer_key = load_answer_keys(answer_key_path)
    results = {}
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, file_name)
            try:
                score = grade_omr_image(img_path, answer_key)
                results[file_name] = score
            except Exception as e:
                results[file_name] = f"Error: {e}"
    return results
