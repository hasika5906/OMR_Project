"""
omr_scanner.py
Core OMR engine:
- Detects document, warps perspective
- Finds bubbles, groups into questions
- Determines selected choice per question (A-D)
- Flags ambiguous answers
- Returns per-question results and subject-wise scoring
"""

import cv2
import numpy as np
import json
import os
from typing import Tuple, List, Dict

# -------------------------
# Configurable parameters
# -------------------------
NUM_QUESTIONS = 100
QUESTIONS_PER_SUBJECT = 20
NUM_SUBJECTS = 5
CHOICES = 4  # A-D
BUBBLE_MIN_SIZE = 4
BUBBLE_MAX_SIZE = 400
ROW_Y_TOLERANCE = 25
AMBIGUITY_RATIO = 0.65
MIN_FILL_PIXELS = 10
# -------------------------

def order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4,2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = np.argmax(s)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def detect_document_and_warp(image: np.ndarray) -> Tuple[np.ndarray,bool]:
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    edged = cv2.Canny(blur,75,200)
    cnts,_ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:8]
    docCnt=None
    for c in cnts:
        peri = cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,0.02*peri,True)
        if len(approx)==4:
            docCnt=approx
            break
    if docCnt is None:
        return orig, False
    pts = docCnt.reshape(4,2)
    rect = order_points(pts)
    (tl,tr,br,bl)=rect
    maxW = max(int(np.linalg.norm(br-bl)), int(np.linalg.norm(tr-tl)))
    maxH = max(int(np.linalg.norm(tr-br)), int(np.linalg.norm(tl-bl)))
    dst = np.array([[0,0],[maxW-1,0],[maxW-1,maxH-1],[0,maxH-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect,dst)
    warp = cv2.warpPerspective(orig,M,(maxW,maxH))
    return warp, True

def find_bubble_contours(warp: np.ndarray) -> Tuple[np.ndarray,List[np.ndarray]]:
    gray = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray,5)
    th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    cnts,_ = cv2.findContours(th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubble_cnts=[]
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        ar = w/float(h) if h>0 else 0
        if (BUBBLE_MIN_SIZE<=w<=BUBBLE_MAX_SIZE) and (BUBBLE_MIN_SIZE<=h<=BUBBLE_MAX_SIZE) and (0.6<=ar<=1.4):
            bubble_cnts.append(c)
    return th, bubble_cnts

def sort_contours(cnts: List[np.ndarray], method="top-to-bottom") -> List[np.ndarray]:
    reverse=False
    i=0
    if method in ["right-to-left","bottom-to-top"]:
        reverse=True
    if method in ["top-to-bottom","bottom-to-top"]:
        i=1
    boundingBoxes=[cv2.boundingRect(c) for c in cnts]
    cnts_bbs=sorted(zip(cnts,boundingBoxes), key=lambda b:b[1][i], reverse=reverse)
    return [c for c,_ in cnts_bbs]

def group_into_questions(bubble_cnts: List[np.ndarray], choices:int=CHOICES) -> List[List[np.ndarray]]:
    bubble_cnts = sort_contours(bubble_cnts, method="top-to-bottom")
    rows=[]
    current_row=[]
    last_y=None
    for c in bubble_cnts:
        x,y,w,h=cv2.boundingRect(c)
        if last_y is None:
            current_row.append(c)
            last_y=y
            continue
        if abs(y-last_y)<=ROW_Y_TOLERANCE:
            current_row.append(c)
        else:
            rows.append(current_row)
            current_row=[c]
            last_y=y
    if current_row:
        rows.append(current_row)
    questions=[]
    for row in rows:
        row_sorted=sorted(row,key=lambda c:cv2.boundingRect(c)[0])
        for i in range(0,len(row_sorted),choices):
            group=row_sorted[i:i+choices]
            if len(group)==choices:
                questions.append(group)
    return questions

def analyze_image(warp: np.ndarray, answer_key: Dict[str,str], choices:int=CHOICES) -> Dict:
    th,bubble_cnts=find_bubble_contours(warp)
    questions=group_into_questions(bubble_cnts, choices=choices)
    if len(questions)!=NUM_QUESTIONS:
        sorted_all=sort_contours(bubble_cnts, method="top-to-bottom")
        fallback_qs=[]
        for i in range(0,len(sorted_all),choices):
            group=sorted_all[i:i+choices]
            if len(group)==choices:
                fallback_qs.append(group)
        if len(fallback_qs)==NUM_QUESTIONS:
            questions=fallback_qs

    results=[]
    canvas=warp.copy()
    th_color=cv2.cvtColor(th, cv2.COLOR_GRAY2BGR)
    canvas=cv2.addWeighted(canvas,0.8,th_color,0.2,0)

    for q_idx, group in enumerate(questions[:NUM_QUESTIONS], start=1):
        q_group_sorted=sort_contours(group, method="left-to-right")
        fill_pixels_per_choice=[]
        selected_idx=None
        for c in q_group_sorted:
            mask=np.zeros(th.shape, dtype='uint8')
            cv2.drawContours(mask,[c],-1,255,-1)
            filled=cv2.countNonZero(cv2.bitwise_and(th,th,mask=mask))
            fill_pixels_per_choice.append(filled)
        if len(fill_pixels_per_choice)>0:
            best_idx=int(np.argmax(fill_pixels_per_choice))
            best_val=fill_pixels_per_choice[best_idx]
            second_val=max([v for i,v in enumerate(fill_pixels_per_choice) if i!=best_idx], default=0)
            if best_val<MIN_FILL_PIXELS:
                selected_idx=None
                ambiguous=False
            else:
                ambiguous=(second_val/float(best_val+1e-6))>AMBIGUITY_RATIO
                selected_idx=best_idx if not ambiguous else None
        selected_label=chr(ord('A')+selected_idx) if selected_idx is not None else None
        for i,c in enumerate(q_group_sorted):
            x,y,w,h=cv2.boundingRect(c)
            center=(x+w//2,y+h//2)
            color=(180,180,180)
            thickness=1
            if selected_idx==i:
                color=(0,200,0)
                thickness=2
            elif selected_label is None and fill_pixels_per_choice[i]>=MIN_FILL_PIXELS:
                color=(0,180,255)
                thickness=2 if fill_pixels_per_choice[i]>MIN_FILL_PIXELS else 1
            cv2.rectangle(canvas,(x,y),(x+w,y+h),color,thickness)
            cv2.putText(canvas, chr(ord('A')+i),(x+3,y+h+14),cv2.FONT_HERSHEY_SIMPLEX,0.45,color,1)
        res={"question":q_idx,"selected_index":selected_idx,"selected_label":selected_label,
             "fill_pixels":fill_pixels_per_choice,"ambiguous":ambiguous if 'ambiguous' in locals() else False}
        results.append(res)
    while len(results)<NUM_QUESTIONS:
        q_idx=len(results)+1
        results.append({"question":q_idx,"selected_index":None,"selected_label":None,"fill_pixels":[],"ambiguous":False})
    return {"canvas":canvas,"results":results,"thresh":th}

def grade_results(results: List[Dict], answer_key_for_version: Dict[str,str]) -> Dict:
    per_q=[]
    subject_scores=[0]*NUM_SUBJECTS
    total_attempted=0
    total_correct=0
    for r in results:
        q=r["question"]
        selected=r["selected_label"]
        correct=answer_key_for_version.get(str(q), None)
        is_correct=None
        if correct is not None:
            if selected is None:
                is_correct=False
            else:
                is_correct=(selected==correct)
            if is_correct:
                total_correct+=1
                subj_index=(q-1)//QUESTIONS_PER_SUBJECT
                if 0<=subj_index<NUM_SUBJECTS:
                    subject_scores[subj_index]+=1
            total_attempted+=1
        per_q.append({"question":q,"selected":selected,"correct":correct,"is_correct":is_correct,"ambiguous":r["ambiguous"]})
    total_score=sum(subject_scores)
    return {"per_question":per_q,"subject_scores":subject_scores,"total_score":total_score,
            "total_correct":total_correct,"total_marked_questions_in_key":len(answer_key_for_version)}

def load_answer_keys(path:str) -> Dict:
    with open(path,'r') as f:
        data=json.load(f)
    return data

# -------------------------
# Main runner
# -------------------------
if __name__=="__main__":
    BASE_FOLDER = r".\OMR_sheets"
    ANSWER_KEYS = {"SetA": r".\answer_key_A.json", "SetB": r".\answer_key_B.json"}
    version="v1"
    SHOW_VISUAL=False

    for set_name in ["SetA","SetB"]:
        print(f"=== Processing {set_name} ===")
        sheet_folder=os.path.join(BASE_FOLDER,set_name)
        answer_key_path=ANSWER_KEYS[set_name]
        keys=load_answer_keys(answer_key_path)
        key_for_version=keys.get(version, {})
        for sheet_file in os.listdir(sheet_folder):
            if not sheet_file.lower().endswith(('.jpg','.jpeg','.png')):
                continue
            print("Checking file:", sheet_file)
            img_path=os.path.join(sheet_folder,sheet_file)
            img=cv2.imread(img_path)
            if img is None:
                print("Could not open image:", img_path)
                continue
            warp,found=detect_document_and_warp(img)
            if not found:
                print("Warning: Document not detected properly:", sheet_file)
            data=analyze_image(warp, {}, choices=CHOICES)
            grading=grade_results(data["results"], key_for_version)
            print(f"Sheet: {sheet_file} | Total Score: {grading['total_score']} | Subject Scores: {grading['subject_scores']}")
            out_prefix=os.path.join(sheet_folder, sheet_file.split('.')[0])
            cv2.imwrite(f"{out_prefix}_graded.jpg", data["canvas"])
            with open(f"{out_prefix}_results.json","w") as f:
                json.dump({"grading":grading,"per_question":grading["per_question"]},f,indent=2)
            print(f"Saved: {out_prefix}_graded.jpg, {out_prefix}_results.json\n")
            if SHOW_VISUAL:
                cv2.imshow("Detected Bubbles", data["canvas"])
                cv2.waitKey(0)
                cv2.destroyAllWindows()
import os

def process_omr_folder(folder_path, answer_key_path):
    """
    Process all OMR images in a folder using a given answer key.
    Returns a dictionary {filename: score}.
    """
    from omr_scanner import load_answer_keys, grade_omr_image  # adjust if your grading function name differs

    # Load answer key
    answer_key = load_answer_keys(answer_key_path)

    results = {}
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, file_name)
            try:
                # grade_omr_image should return the score
                score = grade_omr_image(img_path, answer_key)
                results[file_name] = score
            except Exception as e:
                results[file_name] = f"Error: {e}"

    return results

