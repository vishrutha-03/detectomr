import json

def generate_complete_template(version="v1"):
    """Generate complete template with all 100 questions (20 per subject × 5 subjects)"""

    # Base coordinates for first column (Python)
    base_y_positions = [0.20, 0.25, 0.30, 0.35, 0.40, 0.55, 0.60, 0.65, 0.70, 0.75,
                       0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25]

    # Column x-positions for 5 subjects
    column_x_positions = [0.10, 0.16, 0.22, 0.28]  # A, B, C, D

    bubbles = []

    # Generate bubbles for all 5 subjects (100 questions total)
    for subject in range(5):
        subject_name = ["Python", "EDA", "SQL", "POWER BI", "Statistics"][subject]
        q_start = subject * 20 + 1

        # Use different y-positions for each subject to avoid overlap
        y_offset = subject * 0.3  # Offset each column vertically

        for q in range(20):
            q_num = q_start + q
            y_pos = base_y_positions[q] + y_offset

            for opt_idx, x_pos in enumerate(column_x_positions):
                option = ["A", "B", "C", "D"][opt_idx]
                bubbles.append({
                    "q": q_num,
                    "option": option,
                    "bbox": [x_pos, y_pos, 0.04, 0.03]
                })

    template = {
        "version": version,
        "subjects": [
            {"name": "Python", "q_start": 1, "q_count": 20},
            {"name": "EDA", "q_start": 21, "q_count": 20},
            {"name": "SQL", "q_start": 41, "q_count": 20},
            {"name": "POWER BI", "q_start": 61, "q_count": 20},
            {"name": "Statistics", "q_start": 81, "q_count": 20}
        ],
        "bubbles": bubbles
    }

    return template

def generate_complete_template_setb():
    """Generate complete template for Set B with different bubble positions"""

    # Different base coordinates for Set B
    base_y_positions = [0.18, 0.24, 0.30, 0.36, 0.42, 0.60, 0.66, 0.72, 0.78, 0.84]

    # Column x-positions for Set B (slightly different)
    column_x_positions = [0.12, 0.18, 0.24, 0.30]  # A, B, C, D

    bubbles = []

    # Generate bubbles for all 5 subjects (100 questions total)
    for subject in range(5):
        subject_name = ["Python", "EDA", "SQL", "POWER BI", "Statistics"][subject]
        q_start = subject * 20 + 1

        # Use different y-positions for each subject to avoid overlap
        y_offset = subject * 0.3  # Offset each column vertically

        for q in range(20):
            q_num = q_start + q
            y_pos = base_y_positions[q] + y_offset

            for opt_idx, x_pos in enumerate(column_x_positions):
                option = ["A", "B", "C", "D"][opt_idx]
                bubbles.append({
                    "q": q_num,
                    "option": option,
                    "bbox": [x_pos, y_pos, 0.04, 0.035]
                })

    template = {
        "version": "v2",
        "subjects": [
            {"name": "Python", "q_start": 1, "q_count": 20},
            {"name": "EDA", "q_start": 21, "q_count": 20},
            {"name": "SQL", "q_start": 41, "q_count": 20},
            {"name": "POWER BI", "q_start": 61, "q_count": 20},
            {"name": "Statistics", "q_start": 81, "q_count": 20}
        ],
        "bubbles": bubbles
    }

    return template

def generate_answer_keys():
    """Generate answer keys for both Set A and Set B"""

    # Set A answers (from the first image)
    seta_answers = {
        "1": "A", "2": "C", "3": "C", "4": "C", "5": "C", "6": "A", "7": "C", "8": "C", "9": "B", "10": "C",
        "11": "A", "12": "A", "13": "D", "14": "A", "15": "B", "16": "A,B,C,D", "17": "C", "18": "D", "19": "A", "20": "B",
        "21": "A", "22": "D", "23": "B", "24": "A", "25": "B", "26": "B", "27": "A", "28": "B", "29": "D", "30": "C",
        "31": "C", "32": "A", "33": "B", "34": "C", "35": "A", "36": "B", "37": "D", "38": "B", "39": "B", "40": "C",
        "41": "C", "42": "C", "43": "C", "44": "B", "45": "B", "46": "A", "47": "C", "48": "B", "49": "D", "50": "A",
        "51": "C", "52": "B", "53": "C", "54": "C", "55": "A", "56": "B", "57": "B", "58": "A", "59": "B", "60": "B",
        "61": "B", "62": "C", "63": "A", "64": "D", "65": "C", "66": "B", "67": "B", "68": "A", "69": "C", "70": "B",
        "71": "B", "72": "B", "73": "D", "74": "B", "75": "A", "76": "B", "77": "B", "78": "A", "79": "B", "80": "B",
        "81": "A", "82": "B", "83": "C", "84": "B", "85": "C", "86": "B", "87": "B", "88": "B", "89": "A", "90": "B",
        "91": "C", "92": "B", "93": "C", "94": "D", "95": "B", "96": "B", "97": "C", "98": "A", "99": "B", "100": "C"
    }

    # Set B answers (from the second image)
    setb_answers = {
        "1": "B", "2": "A", "3": "D", "4": "B", "5": "B", "6": "D", "7": "C", "8": "C", "9": "A", "10": "C",
        "11": "C", "12": "B", "13": "D", "14": "C", "15": "A", "16": "A", "17": "C", "18": "B", "19": "D", "20": "C",
        "21": "B", "22": "A", "23": "D", "24": "B", "25": "B", "26": "D", "27": "C", "28": "C", "29": "A", "30": "C",
        "31": "C", "32": "B", "33": "D", "34": "C", "35": "A", "36": "A", "37": "C", "38": "B", "39": "D", "40": "C",
        "41": "C", "42": "C", "43": "C", "44": "B", "45": "B", "46": "A", "47": "C", "48": "B", "49": "D", "50": "A",
        "51": "C", "52": "B", "53": "C", "54": "C", "55": "A", "56": "B", "57": "B", "58": "A", "59": "B", "60": "B",
        "61": "B", "62": "C", "63": "A", "64": "D", "65": "C", "66": "B", "67": "B", "68": "A", "69": "C", "70": "B",
        "71": "B", "72": "B", "73": "D", "74": "B", "75": "A", "76": "B", "77": "B", "78": "A", "79": "B", "80": "B",
        "81": "A", "82": "B", "83": "C", "84": "B", "85": "C", "86": "B", "87": "B", "88": "B", "89": "A", "90": "B",
        "91": "C", "92": "B", "93": "C", "94": "D", "95": "B", "96": "B", "97": "C", "98": "A", "99": "B", "100": "C"
    }

    return seta_answers, setb_answers

if __name__ == "__main__":
    # Generate complete template for Set A
    template_a = generate_complete_template("v1")

    # Generate complete template for Set B
    template_b = generate_complete_template_setb()

    # Generate answer keys
    seta_answers, setb_answers = generate_answer_keys()

    # Save template to seta.json
    with open("templates/seta.json", "w") as f:
        json.dump(template_a, f, indent=2)

    # Save template to setb.json
    with open("templates/setb.json", "w") as f:
        json.dump(template_b, f, indent=2)

    # Save answer keys
    with open("templates/answers_v1.json", "w") as f:
        json.dump(seta_answers, f, indent=2)

    with open("templates/answers_v2.json", "w") as f:
        json.dump(setb_answers, f, indent=2)

    print("✅ Complete templates and answer keys generated successfully!")
    print(f"📊 Set A template includes {len(template_a['bubbles'])} bubble definitions")
    print(f"📊 Set B template includes {len(template_b['bubbles'])} bubble definitions")
    print(f"📝 Set A has {len(seta_answers)} answers")
    print(f"📝 Set B has {len(setb_answers)} answers")
