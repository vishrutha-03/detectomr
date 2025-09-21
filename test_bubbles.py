#!/usr/bin/env python3
"""
Test script to debug bubble detection issues
"""
import cv2
import numpy as np
import json
import os
from omr.detectbub_fixed import detect_from_template, is_marked

def test_bubble_detection():
    """Test bubble detection with a sample image"""

    # Load a test image
    test_image = "test_omr.jpg"  # You'll need to provide this

    if not os.path.exists(test_image):
        print(f"Test image {test_image} not found. Please provide a test OMR image.")
        return

    # Load the image
    img = cv2.imread(test_image)
    if img is None:
        print("Could not load test image")
        return

    # Load template
    template_file = "templates/setb.json"
    if not os.path.exists(template_file):
        print(f"Template file {template_file} not found")
        return

    with open(template_file, 'r') as f:
        template = json.load(f)

    print(f"Loaded template with {len(template['bubbles'])} bubbles")

    # Test bubble detection
    try:
        detected, ambiguous = detect_from_template(img, template)
        print(f"Detection completed. Found {len(ambiguous)} ambiguous bubbles")

        if ambiguous:
            print("Ambiguous bubbles:")
            for amb in ambiguous[:5]:  # Show first 5
                print(f"  Q{amb['q']} Option {amb['option']}: {amb['reason']}")

        # Count marked bubbles
        total_marked = 0
        for q, opts in detected.items():
            marked = [opt for opt, st in opts.items() if st is True]
            if marked:
                total_marked += 1

        print(f"Total marked bubbles detected: {total_marked}")

    except Exception as e:
        print(f"Error during bubble detection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bubble_detection()
