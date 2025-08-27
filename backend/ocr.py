import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import tempfile

# Configure Tesseract path (adjust based on system)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/Mac

def preprocess_image(image_path):
    """
    Enhanced preprocessing for better OCR results
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"[OCR] Warning: Could not read image at {image_path}")
            return image_path
        
        print(f"[OCR] Original image shape: {image.shape}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize image if too small (improve OCR accuracy)
        height, width = gray.shape
        if height < 600 or width < 600:
            scale_factor = max(600/height, 600/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            print(f"[OCR] Resized image to: {gray.shape}")
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Apply thresholding to get better text contrast
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Save preprocessed image
        preprocessed_path = image_path.replace('.jpg', '_preprocessed.jpg')
        cv2.imwrite(preprocessed_path, cleaned)
        print(f"[OCR] Preprocessed image saved to: {preprocessed_path}")
        
        return preprocessed_path
        
    except Exception as e:
        print(f"[OCR] Preprocessing error: {e}")
        return image_path

def extract_text_from_image(image_path):
    """
    Extract text from food label image using Tesseract OCR
    """
    try:
        # Preprocess image for better OCR
        preprocessed_path = preprocess_image(image_path)
        
        # Configure OCR settings
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz()[]{}.,;:!?%+-*/= \n\t'
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(
            Image.open(preprocessed_path),
            config=custom_config,
            lang='eng'
        )
        
        # Clean up preprocessed file
        if preprocessed_path != image_path:
            try:
                os.unlink(preprocessed_path)
            except OSError:
                pass
        
        # Clean and normalize extracted text
        cleaned_text = clean_extracted_text(text)
        
        return cleaned_text
        
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return ""

def clean_extracted_text(text):
    """
    Clean and normalize extracted OCR text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:  # Skip empty lines
            lines.append(line)
    
    # Join lines with single newlines
    cleaned_text = '\n'.join(lines)
    
    # Fix common OCR errors
    replacements = {
        'Calones': 'Calories',
        'Calone': 'Calorie',
        'Proteln': 'Protein',
        'Sodlum': 'Sodium',
        'Flber': 'Fiber',
        'Sugars': 'Sugar',
        'Fat': 'Fat',
        'Cholesterol': 'Cholesterol',
        'Carbohydrate': 'Carbohydrates',
        'Vitamin': 'Vitamin',
        'Mlneral': 'Mineral',
        'lngredients': 'Ingredients',
        'Ingredlents': 'Ingredients',
        '0g': '0g',
        '1g': '1g',
        '2g': '2g',
        '3g': '3g',
        '4g': '4g',
        '5g': '5g',
        '6g': '6g',
        '7g': '7g',
        '8g': '8g',
        '9g': '9g',
        'mg': 'mg',
        'mcg': 'mcg',
        'IU': 'IU',
        '%': '%',
        'Daily Value': 'Daily Value',
        'DV': 'DV',
        'Serving Size': 'Serving Size',
        'Servings Per Container': 'Servings Per Container',
    }
    
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    return cleaned_text

def extract_text_with_confidence(image_path):
    """
    Extract text with confidence scores for quality assessment
    """
    try:
        preprocessed_path = preprocess_image(image_path)
        
        # Get detailed data including confidence scores
        data = pytesseract.image_to_data(
            Image.open(preprocessed_path),
            output_type=pytesseract.Output.DICT,
            lang='eng'
        )
        
        # Filter high-confidence text
        high_confidence_text = []
        for i, conf in enumerate(data['conf']):
            if int(conf) > 30:  # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    high_confidence_text.append(text)
        
        # Clean up
        if preprocessed_path != image_path:
            try:
                os.unlink(preprocessed_path)
            except OSError:
                pass
        
        return ' '.join(high_confidence_text)
        
    except Exception as e:
        print(f"Confidence-based OCR error: {e}")
        return extract_text_from_image(image_path)  # Fallback to basic OCR
