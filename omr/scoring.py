import json
import math
import os

def load_answer_key(path):
    with open(path, "r") as f:
        return json.load(f)

def compute_scores(detected_answers, template, answer_key, per_subject_max=20):
    """
    detected_answers: dict {q: {opt: True/False/None}}
    template: template JSON (with 'subjects' list)
    answer_key: dict mapping question "1" -> "A" etc (strings)
    Returns:
      per_subject_score: {subject_name: score_out_of_20}
      total_score_0_100: float
      per_question_result: {q: {'selected': 'A' or None, 'correct': True/False/None}}
    """
    # Build quick map of selected option per q
    def get_selected(opt_dict):
        marked = [opt for opt, st in opt_dict.items() if st is True]
        if len(marked) == 1:
            return marked[0]
        # if none marked, or multiple, treat as None (can be flagged)
        return None

    per_question_result = {}
    for q, opts in detected_answers.items():
        selected = get_selected(opts)
        correct_ans = answer_key.get(str(q))
        if selected is None:
            correct = None
        else:
            correct = (selected == correct_ans)
        per_question_result[int(q)] = {'selected': selected, 'correct': correct}

    # For each subject, count correct raw, then scale to per_subject_max
    per_subject_score = {}
    total_raw = 0
    total_max_raw = 0
    for s in template['subjects']:
        name = s['name']
        q_start = int(s['q_start'])
        q_count = int(s['q_count'])
        raw_correct = 0
        for qi in range(q_start, q_start + q_count):
            res = per_question_result.get(qi)
            if res is None:
                # no detection info -> treat as incorrect
                pass
            else:
                if res['correct'] is True:
                    raw_correct += 1
        per_subject_max_raw = q_count
        # scale to per_subject_max (eg 20)
        score = (raw_correct / per_subject_max_raw) * per_subject_max if per_subject_max_raw > 0 else 0
        per_subject_score[name] = round(score, 2)
        total_raw += raw_correct
        total_max_raw += per_subject_max_raw

    # total: scale combined raw to 100
    total_score_0_100 = round((total_raw / total_max_raw) * 100 if total_max_raw > 0 else 0, 2)

    return per_subject_score, total_score_0_100, per_question_result
