# OMR Bubbles Error Fix

## Problem
The OMR system was throwing "bubbles error" when uploading files. This was caused by several issues in the bubble detection logic.

## Root Causes Identified

1. **Insufficient error handling** in `detectbub.py`
2. **Poor bounds checking** for bubble coordinates
3. **Missing validation** for template structure
4. **Inadequate error reporting** in the main app
5. **Threshold values** not suitable for all image types

## Files Created/Modified

### 1. `omr/detectbub_fixed.py` (NEW)
- **Improved error handling** with comprehensive try-catch blocks
- **Better bounds checking** for bubble coordinates
- **Template validation** to ensure required keys exist
- **Detailed error reporting** for debugging
- **Safer image processing** with null checks

### 2. `app_fixed.py` (NEW)
- **Enhanced error handling** throughout the processing pipeline
- **Better user feedback** with detailed error messages
- **Improved template loading** with fallback mechanisms
- **Ambiguous bubble reporting** to help identify issues
- **Full traceback display** for debugging

### 3. `test_bubbles.py` (NEW)
- **Standalone testing script** to debug bubble detection
- **Template validation** testing
- **Error reproduction** capabilities

## How to Fix the Error

### Option 1: Quick Fix (Recommended)
1. **Replace the main app file**:
   ```bash
   mv app.py app_original.py
   mv app_fixed.py app.py
   ```

2. **Replace the bubble detection module**:
   ```bash
   mv omr/detectbub.py omr/detectbub_original.py
   mv omr/detectbub_fixed.py omr/detectbub.py
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

### Option 2: Test First
1. **Run the test script** to identify specific issues:
   ```bash
   python test_bubbles.py
   ```

2. **Apply fixes based on test results**

## Common Error Scenarios & Solutions

### 1. "Template missing 'bubbles' key"
**Problem**: Template JSON is malformed
**Solution**: Check your template file structure matches the expected format

### 2. "Invalid input image for bubble detection"
**Problem**: Image preprocessing failed
**Solution**: Ensure the uploaded image is a valid OMR sheet

### 3. "Could not decode image file"
**Problem**: Corrupted or unsupported image format
**Solution**: Use JPG, JPEG, or PNG formats

### 4. "crop-empty" errors
**Problem**: Bubble coordinates are outside image bounds
**Solution**: The new code handles this gracefully by marking as ambiguous

## Template Format Requirements

Your template JSON must have this structure:
```json
{
  "version": "v2",
  "subjects": [...],
  "bubbles": [
    {
      "q": 1,
      "option": "A",
      "bbox": [0.12, 0.18, 0.04, 0.035]
    }
  ]
}
```

## Answer Key Requirements

Answer keys should be in separate files named `answers_{version}.json`:
```json
{
  "1": "A",
  "2": "C",
  "3": "B"
}
```

## Testing Your Fix

1. **Upload a known good OMR image**
2. **Check the console for error messages**
3. **Look for "ambiguous bubbles" warnings** - these indicate detection issues
4. **Verify the overlay shows correct bubble positions**

## Performance Improvements

The fixed version includes:
- **Better threshold handling** (adjustable low_thresh/high_thresh)
- **Improved image processing** with Gaussian blur and morphology
- **Memory efficient** crop operations
- **Faster error recovery**

## Troubleshooting Tips

1. **Check image quality**: Ensure good lighting and clear bubble marks
2. **Verify template coordinates**: Use the overlay to check if bubbles align
3. **Adjust thresholds**: Modify `low_thresh` and `high_thresh` if needed
4. **Check file permissions**: Ensure read access to template files

## Getting Help

If you still encounter issues:
1. Run `python test_bubbles.py` for detailed diagnostics
2. Check the Streamlit console for full error traces
3. Verify your template and answer key files are properly formatted
4. Ensure OpenCV and other dependencies are properly installed

## Dependencies

Make sure you have:
- opencv-python
- numpy
- streamlit
- pandas (for batch processing)

Install with:
```bash
pip install opencv-python numpy streamlit pandas
