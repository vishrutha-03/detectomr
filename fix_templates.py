#!/usr/bin/env python3
"""
Fix template coordinates to be within [0,1] range
"""
import json
import os

def fix_template_coordinates(template_path):
    """Fix bubble coordinates in a template file"""
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)

        print(f"\nFixing coordinates in {template_path}:")

        fixed_bubbles = []
        max_y = 0

        for bubble in template['bubbles']:
            bbox = bubble['bbox']
            x, y, w, h = bbox

            # Find the maximum y coordinate to understand the scale
            if y > max_y:
                max_y = y

            fixed_bubbles.append(bubble.copy())

        # Calculate scale factor if coordinates exceed 1.0
        scale_factor = 1.0
        if max_y > 1.0:
            scale_factor = 1.0 / max_y
            print(f"  Scaling coordinates by factor: {scale_factor}")

        # Apply scaling to all bubbles
        for bubble in fixed_bubbles:
            bbox = bubble['bbox']
            x, y, w, h = bbox
            bubble['bbox'] = [x * scale_factor, y * scale_factor, w * scale_factor, h * scale_factor]

        # Update template with fixed bubbles
        template['bubbles'] = fixed_bubbles

        # Save fixed template
        fixed_path = template_path.replace('.json', '_fixed.json')
        with open(fixed_path, 'w') as f:
            json.dump(template, f, indent=2)

        print(f"  ✅ Fixed template saved to: {fixed_path}")
        return True

    except Exception as e:
        print(f"  ❌ Error fixing {template_path}: {e}")
        return False

def main():
    """Main function to fix all templates"""
    print("🔧 Template Coordinate Fixer")
    print("=" * 40)

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

    # Fix all templates
    all_fixed = True
    for tf in template_files:
        if not fix_template_coordinates(os.path.join(template_dir, tf)):
            all_fixed = False

    print("\n" + "=" * 40)
    if all_fixed:
        print("✅ All templates fixed successfully!")
        print("\nNext steps:")
        print("1. Replace original template files with _fixed.json versions")
        print("2. Run 'python validate_templates.py' to verify fixes")
        print("3. Test with your OMR application")
    else:
        print("❌ Some templates could not be fixed!")

if __name__ == "__main__":
    main()
