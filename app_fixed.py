import streamlit as st
import cv2
import numpy as np
import json
import os
import traceback
from omr.preprocess import detect_sheet_and_warp, read_qr_version
from omr.detectbub_fixed import detect_from_template, bbox_norm_to_px, choose_selected_option
from omr.scoring import load_answer_key, compute_scores

# Create results folder
os.makedirs("results", exist_ok=True)
os.makedirs("results/images", exist_ok=True)
os.makedirs("results/overlays", exist_ok=True)

st.set_page_config(layout="wide", page_title="OMR Evaluator")

st.title("📄 Automated OMR Evaluation — MVP")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded = st.file_uploader("Upload OMR image (single)", type=["jpg", "jpeg", "png"])
    uploaded_multi = st.file_uploader("Or upload multiple (zip not supported here) - multi select", accept_multiple_files=True, type=["jpg","jpeg","png"])

with col2:
    # Only include template files (not answer key files)
    template_files = [f for f in os.listdir("templates") if f.endswith(".json") and not f.startswith("answers_")]
    template_choice = st.selectbox("Choose template (or use QR on sheet)", template_files)

# helper to load template JSON
def load_template(fn):
    try:
        with open(os.path.join("templates", fn), "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading template {fn}: {e}")
        return None

def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

def draw_overlay(warped_bgr, template, per_question_result):
    overlay = warped_bgr.copy()
    h, w = overlay.shape[:2]
    # draw rectangles and mark selected / correct
    for entry in template['bubbles']:
        q = int(entry['q']); opt = entry.get('option')
        x, y, bw, bh = bbox_norm_to_px(entry['bbox'], w, h)
        # default color light gray
        color = (200, 200, 200)
        # if selected
        pr = per_question_result.get(q, {})
        sel = pr.get('selected')
        correct = pr.get('correct')
        if sel is not None and opt == sel:
            # green for correct, red for wrong
            if correct is True:
                color = (0, 200, 0)
            elif correct is False:
                color = (0, 0, 255)
            else:
                color = (0, 200, 200)  # ambiguous
        cv2.rectangle(overlay, (x, y), (x + bw, y + bh), color, 2)
    return overlay

def process_single_file(file_bytes, template_fn):
    try:
        arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image file")

        warped = detect_sheet_and_warp(img)

        if warped is None:
            raise ValueError("Could not detect and warp the sheet")

        # try QR detection
        version_from_qr = read_qr_version(warped)
        if version_from_qr:
            # try find matching template file
            matching = [f for f in template_files if version_from_qr in f or version_from_qr in f.replace(".json","")]
            if matching:
                template_use = load_template(matching[0])
                if template_use:
                    st.info(f"Using QR-detected template: {matching[0]}")
            else:
                template_use = load_template(template_fn)
        else:
            template_use = load_template(template_fn)

        if template_use is None:
            raise ValueError("Could not load template")

        # detect bubbles
        detected, ambiguous = detect_from_template(warped, template_use)

        # compute selected per question
        per_question_selected = {}
        for q, opts in detected.items():
            sel = choose_selected_option(opts)
            per_question_selected[int(q)] = {'selected': sel, 'correct': None}

        # load answer key file for template
        answer_key_raw = {}
        # look for "answers" in template file or side-by-side answer key file named key_<template_fn>
        if 'answers' in template_use:
            answer_key_raw = template_use['answers']
        else:
            # try answers_{version}.json
            v = template_use.get('version')
            if v:
                candidate = f"templates/answers_{v}.json"
                if os.path.exists(candidate):
                    try:
                        with open(candidate) as f:
                            answer_key_raw = json.load(f)
                    except Exception as e:
                        st.warning(f"Could not load answer key {candidate}: {e}")

        if not answer_key_raw:
            st.warning("No answer key found - scores will not be calculated")
            per_question_result = per_question_selected
            per_subject_score = {}
            total_score = 0
        else:
            # Now compute scores
            per_subject_score, total_score, per_question_result = compute_scores(detected, template_use, answer_key_raw)

        # Build result dict
        result = {
            "per_subject_score": per_subject_score,
            "total_score": total_score,
            "per_question": per_question_result,
            "ambiguous_count": len(ambiguous),
            "template_used": template_use.get('version', template_fn)
        }

        return warped, template_use, result, ambiguous

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.error(f"Full traceback: {traceback.format_exc()}")
        return None, None, None, []

# handle single file
if uploaded is not None:
    template_fn = template_choice
    bytes_data = uploaded.getvalue()
    warped, template_use, result, ambiguous = process_single_file(bytes_data, template_fn)

    if warped is not None and result is not None:
        st.subheader("Warped Sheet Preview")
        st.image(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB), use_container_width=True)

        if ambiguous:
            st.warning(f"Found {len(ambiguous)} ambiguous bubbles. Check the overlay for details.")

        st.subheader("Automated result")
        st.json(result)

        # draw overlay
        overlay = draw_overlay(warped, template_use, result['per_question'])
        st.subheader("Overlay (green=correct, red=wrong, gray=not selected)")
        st.image(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB), use_container_width=True)

        # Save outputs
        idx = len(os.listdir("results/images")) + 1
        img_path = f"results/images/warped_{idx}.png"
        ov_path = f"results/overlays/overlay_{idx}.png"
        json_path = f"results/result_{idx}.json"
        cv2.imwrite(img_path, warped)
        cv2.imwrite(ov_path, overlay)
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)

        st.success(f"Saved warped image -> {img_path}, overlay -> {ov_path}, result -> {json_path}")

        if warped is not None and template_use is not None:
            debug_overlay = warped.copy()
            h, w = debug_overlay.shape[:2]
            for entry in template_use['bubbles']:
                x, y, bw, bh = bbox_norm_to_px(entry['bbox'], w, h)
                cv2.rectangle(debug_overlay, (x, y), (x + bw, y + bh), (255, 0, 0), 2)
            st.image(cv2.cvtColor(debug_overlay, cv2.COLOR_BGR2RGB), caption="Bubble positions overlay", use_container_width=True)

# handle multiple files (simple loop)
if uploaded_multi:
    st.info(f"Processing {len(uploaded_multi)} files...")
    template_fn = template_choice
    csv_rows = []
    for f in uploaded_multi:
        try:
            warped, template_use, result, ambiguous = process_single_file(f.getvalue(), template_fn)
            if warped is not None and result is not None:
                idx = len(os.listdir("results/images")) + 1
                img_path = f"results/images/warped_{idx}.png"
                ov_path = f"results/overlays/overlay_{idx}.png"
                json_path = f"results/result_{idx}.json"
                cv2.imwrite(img_path, warped)
                overlay = draw_overlay(warped, template_use, result['per_question'])
                cv2.imwrite(ov_path, overlay)
                with open(json_path, "w") as jf:
                    json.dump(result, jf, indent=2)
                csv_rows.append({"file": f.name, "total": result['total_score']})
        except Exception as e:
            st.error(f"Error processing {f.name}: {e}")

    # save CSV
    if csv_rows:
        import pandas as pd
        df = pd.DataFrame(csv_rows)
        csv_path = "results/batch_results.csv"
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        st.success(f"Batch done, results at {csv_path}")
