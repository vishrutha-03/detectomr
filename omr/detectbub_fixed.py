import cv2
import numpy as np

def bbox_norm_to_px(bbox_norm, width, height):
    """Convert normalized bbox coordinates to pixel coordinates"""
    xn, yn, wn, hn = bbox_norm
    x = int(xn * width)
    y = int(yn * height)
    w = int(wn * width)
    h = int(hn * height)
    return x, y, w, h

def is_marked(crop_gray):
    """Return filled_ratio (0..1) and binary image used"""
    if crop_gray.size == 0:
        return 0, None

    blur = cv2.GaussianBlur(crop_gray, (3, 3), 0)
    # Otsu threshold helps adapt to lighting
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Clean tiny noise
    kernel = np.ones((3, 3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    filled = cv2.countNonZero(th)
    area = th.shape[0] * th.shape[1]
    ratio = filled / float(area) if area > 0 else 0
    return ratio, th

def detect_from_template(warped_bgr, template, low_thresh=0.12, high_thresh=0.40):
    """
    warped_bgr: warped top-down image
    template: loaded JSON template (with 'bubbles' list)
    returns: answers dict {q: {option: state}} where state True/False/None (ambiguous),
             ambiguous list with crop images for review
    """
    if warped_bgr is None or warped_bgr.size == 0:
        raise ValueError("Invalid input image for bubble detection")

    gray = cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    if h == 0 or w == 0:
        raise ValueError("Image has zero dimensions")

    answers = {}
    ambiguous = []

    # Validate template structure
    if 'bubbles' not in template:
        raise ValueError("Template missing 'bubbles' key")

    bubbles = template['bubbles']
    if not bubbles:
        raise ValueError("Template has no bubbles defined")

    for entry in bubbles:
        try:
            q = int(entry['q'])
            opt = entry.get('option')
            bbox = entry.get('bbox')

            if bbox is None:
                ambiguous.append({'q': q, 'option': opt, 'reason': 'missing-bbox'})
                answers.setdefault(q, {})[opt] = None
                continue

            x, y, bw, bh = bbox_norm_to_px(bbox, w, h)

            # clip bbox inside image with more generous bounds
            x = max(0, min(x, w-1))
            y = max(0, min(y, h-1))
            bw = max(1, min(bw, w - x))
            bh = max(1, min(bh, h - y))

            crop = gray[y:y+bh, x:x+bw]

            if crop.size == 0 or crop.shape[0] == 0 or crop.shape[1] == 0:
                # bad bbox - mark as ambiguous
                answers.setdefault(q, {})[opt] = None
                ambiguous.append({'q': q, 'option': opt, 'reason': 'crop-empty'})
                continue

            ratio, th = is_marked(crop)

            if ratio >= high_thresh:
                state = True
            elif ratio <= low_thresh:
                state = False
            else:
                state = None
                ambiguous.append({'q': q, 'option': opt, 'ratio': ratio, 'crop': crop.tolist() if crop is not None else None})

            answers.setdefault(q, {})[opt] = state

        except (KeyError, ValueError, TypeError) as e:
            ambiguous.append({'q': entry.get('q', 'unknown'), 'option': entry.get('option', 'unknown'), 'reason': f'parsing-error: {str(e)}'})
            continue

    return answers, ambiguous

def choose_selected_option(answer_options):
    """Given dict {opt: True/False/None} choose selected option string or None"""
    marked = [opt for opt, st in answer_options.items() if st is True]
    if len(marked) == 1:
        return marked[0]
    # If zero marked, try highest ratio among None? but here None don't contain ratios.
    # For now treat multiple or zero as None (invalid)
    return None
