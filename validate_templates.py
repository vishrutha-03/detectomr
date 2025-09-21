#!/usr/bin/env python3
"""
Validate template files for OMR system
"""
import json
import os

def validate_template(template_path):
    """Validate a single template file"""
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)

        print(f"\nValidating {template_path}:")

        # Check required keys
        required_keys = ['version', 'subjects', 'bubbles']
        for key in required_keys:
            if key not in template:
                print(f"  ❌ Missing required key: {key}")
                return False
            else:
                print(f"  ✅ Found required key: {key}")

        # Validate version
        version = template.get('version')
        print(f"  📋 Version: {version}")

        # Validate subjects
        subjects = template.get('subjects', [])
        print(f"  📋 Number of subjects: {len(subjects)}")
        for i, subject in enumerate(subjects):
            required_subject_keys = ['name', 'q_start', 'q_count']
            for key in required_subject_keys:
                if key not in subject:
                    print(f"  ❌ Subject {i} missing key: {key}")
                    return False
            print(f"  ✅ Subject {i}: {subject['name']} (Q{subject['q_start']}-{subject['q_start']+subject['q_count']-1})")

        # Validate bubbles
        bubbles = template.get('bubbles', [])
        print(f"  📋 Number of bubbles: {len(bubbles)}")

        # Check for duplicate question numbers
        questions = {}
        for i, bubble in enumerate(bubbles):
            if 'q' not in bubble or 'option' not in bubble or 'bbox' not in bubble:
                print(f"  ❌ Bubble {i} missing required keys (q, option, bbox)")
                return False

            q = bubble['q']
            opt = bubble['option']
            bbox = bubble['bbox']

            if q in questions:
                if opt in questions[q]:
                    print(f"  ❌ Duplicate bubble: Q{q} Option {opt}")
                    return False
                questions[q].append(opt)
            else:
                questions[q] = [opt]

            # Validate bbox format
            if not isinstance(bbox, list) or len(bbox) != 4:
                print(f"  ❌ Bubble Q{q} Option {opt} has invalid bbox format")
                return False

            # Validate bbox values
            if any(not isinstance(x, (int, float)) for x in bbox):
                print(f"  ❌ Bubble Q{q} Option {opt} has non-numeric bbox values")
                return False

            if any(x < 0 or x > 1 for x in bbox):
                print(f"  ❌ Bubble Q{q} Option {opt} has bbox values outside [0,1] range")
                return False

        print(f"  ✅ All bubbles validated successfully")
        return True

    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in {template_path}: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error validating {template_path}: {e}")
        return False

def validate_answer_key(answer_key_path):
    """Validate an answer key file"""
    try:
        with open(answer_key_path, 'r') as f:
            answers = json.load(f)

        print(f"\nValidating {answer_key_path}:")

        if not isinstance(answers, dict):
            print("  ❌ Answer key is not a dictionary")
            return False

        # Check if all values are valid options
        valid_options = ['A', 'B', 'C', 'D']
        for q, ans in answers.items():
            if ans not in valid_options:
                print(f"  ❌ Question {q} has invalid answer '{ans}'. Must be one of {valid_options}")
                return False

        print(f"  ✅ Answer key validated: {len(answers)} questions")
        return True

    except Exception as e:
        print(f"  ❌ Error validating {answer_key_path}: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 OMR Template and Answer Key Validation")
    print("=" * 50)

    # Validate all template files
    template_dir = "templates"
    if not os.path.exists(template_dir):
        print(f"❌ Template directory '{template_dir}' not found")
        return

    template_files = [f for f in os.listdir(template_dir) if f.endswith('.json') and not f.startswith('answers_')]

    if not template_files:
        print(f"❌ No template files found in {template_dir}")
        return

    print(f"Found {len(template_files)} template files:")
    for tf in template_files:
        print(f"  - {tf}")

    # Validate templates
    all_valid = True
    for tf in template_files:
        if not validate_template(os.path.join(template_dir, tf)):
            all_valid = False

    # Validate answer keys
    answer_files = [f for f in os.listdir(template_dir) if f.startswith('answers_') and f.endswith('.json')]
    if answer_files:
        print(f"\nFound {len(answer_files)} answer key files:")
        for af in answer_files:
            print(f"  - {af}")

        for af in answer_files:
            if not validate_answer_key(os.path.join(template_dir, af)):
                all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All validations passed!")
        print("Your templates and answer keys are properly formatted.")
    else:
        print("❌ Some validations failed!")
        print("Please fix the issues above before running the OMR system.")

if __name__ == "__main__":
    main()
