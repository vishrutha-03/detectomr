# Save as calibrate_bubbles.py and run it
import cv2
import json

img = cv2.imread(r"C:\Users\Vishrutha\Downloads\sample.jpg.jpg")  # Use your blank OMR sheet image
img = cv2.resize(img, (2480, 3508))  # Match your template size

bubble_data = []
current_q = 1
options = ['A', 'B', 'C', 'D']

def click_event(event, x, y, flags, param):
    global current_q
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Question {current_q}, Option {options[(len(bubble_data)%4)]}: ({x}, {y})")
        bubble_data.append({
            "q": current_q,
            "option": options[(len(bubble_data)%4)],
            "bbox": [x-50, y-50, 100, 100]  # Changed size to 100x100 for higher intensity
        })
        cv2.circle(img, (x, y), 50, (0,255,0), 2)  # Changed radius to 50 for visual feedback
        cv2.imshow("image", img)
        if len(bubble_data)%4 == 0:
            current_q += 1

cv2.imshow("image", img)
cv2.setMouseCallback("image", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()

with open("templates/calibrated_template.json", "w") as f:
    json.dump({"bubbles": bubble_data}, f, indent=2)