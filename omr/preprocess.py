import cv2
import numpy as np

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def detect_sheet_and_warp(image_bgr, debug=False, output_size=(2480, 3508)):
    """Detects the largest quadrilateral (sheet) and warps. If not found, uses the whole image."""
    orig = image_bgr.copy()
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((5,5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    edged = cv2.Canny(closed, 50, 150)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    img_area = orig.shape[0] * orig.shape[1]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        area = cv2.contourArea(approx)
        # Only accept quadrilaterals that are at least 60% of the image area
        if len(approx) == 4 and area > 0.6 * img_area:
            pts = approx.reshape(4, 2)
            warped = four_point_transform(orig, pts)
            warped = cv2.resize(warped, output_size)
            if debug:
                print("Warped using contour.")
            return warped
    # If no large quadrilateral, just resize the original image (no cropping)
    warped = cv2.resize(orig, output_size)
    if debug:
        print("Fallback: resized original image (no cropping).")
    return warped

def read_qr_version(warped_bgr):
    """Try reading a QR from the warped image. Returns string or None."""
    qr = cv2.QRCodeDetector()
    data, points, _ = qr.detectAndDecode(warped_bgr)
    if data:
        return data.strip()
    return None
