"""
Enhanced OCR module with multiple providers for better nutrition label text extraction
Supports EasyOCR, Google Gemini Vision, and cloud OCR services
"""

import os
import cv2
import numpy as np
import tempfile
import base64
from typing import Dict, List, Optional, Tuple
from PIL import Image
import json

# Optional imports - install as needed
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("EasyOCR not available. Install with: pip install easyocr")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Google Gemini not available. Install with: pip install google-generativeai")

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("Google Cloud Vision not available. Install with: pip install google-cloud-vision")


class EnhancedOCR:
    def __init__(self):
        self.easyocr_reader = None
        self.gemini_model = None
        self.google_vision_client = None
        
        # Initialize available services
        self._init_easyocr()
        self._init_gemini()
        self._init_google_vision()
    
    def _init_easyocr(self):
        """Initialize EasyOCR reader"""
        if EASYOCR_AVAILABLE:
            try:
                print("[OCR] Initializing EasyOCR...")
                self.easyocr_reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if CUDA available
                print("[OCR] EasyOCR initialized successfully")
            except Exception as e:
                print(f"[OCR] EasyOCR initialization failed: {e}")
    
    def _init_gemini(self):
        """Initialize Google Gemini Vision"""
        if GEMINI_AVAILABLE:
            api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    print("[OCR] Google Gemini Vision initialized")
                except Exception as e:
                    print(f"[OCR] Gemini initialization failed: {e}")
            else:
                print("[OCR] Gemini API key not found. Set GOOGLE_AI_API_KEY or GEMINI_API_KEY")
    
    def _init_google_vision(self):
        """Initialize Google Cloud Vision"""
        if GOOGLE_VISION_AVAILABLE:
            try:
                self.google_vision_client = vision.ImageAnnotatorClient()
                print("[OCR] Google Cloud Vision initialized")
            except Exception as e:
                print(f"[OCR] Google Cloud Vision initialization failed: {e}")
    
    def preprocess_image(self, image_path: str) -> str:
        """Enhanced image preprocessing for better OCR results"""
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
            if height < 800 or width < 800:
                scale_factor = max(800/height, 800/width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                print(f"[OCR] Resized image to: {gray.shape}")
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Apply adaptive thresholding for better text contrast
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Save preprocessed image
            preprocessed_path = image_path.replace('.jpg', '_enhanced.jpg')
            cv2.imwrite(preprocessed_path, cleaned)
            print(f"[OCR] Enhanced image saved to: {preprocessed_path}")
            
            return preprocessed_path
            
        except Exception as e:
            print(f"[OCR] Preprocessing error: {e}")
            return image_path
    
    def extract_with_easyocr(self, image_path: str) -> Dict[str, str]:
        """Extract text using EasyOCR"""
        if not self.easyocr_reader:
            return {"error": "EasyOCR not available", "text": ""}
        
        try:
            print("[OCR] Using EasyOCR for text extraction...")
            results = self.easyocr_reader.readtext(image_path, detail=0)
            extracted_text = ' '.join(results)
            
            print(f"[OCR] EasyOCR extracted {len(extracted_text)} characters")
            return {"text": extracted_text, "method": "EasyOCR", "confidence": "high"}
            
        except Exception as e:
            print(f"[OCR] EasyOCR error: {e}")
            return {"error": str(e), "text": ""}
    
    def extract_with_gemini(self, image_path: str) -> Dict[str, str]:
        """Extract nutrition data using Gemini Vision"""
        if not self.gemini_model:
            return {"error": "Gemini not available", "text": ""}
        
        try:
            print("[OCR] Using Gemini Vision for nutrition data extraction...")
            
            # Load and encode image
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            
            prompt = """
            Extract ALL text from this nutrition label image, focusing on:
            1. Nutrition Facts panel data (servings, calories, nutrients, % daily values)
            2. Ingredients list
            3. Any health claims or product information
            4. Brand name and product name
            
            Format the output as clean, structured text that preserves the original layout and numbers exactly as shown.
            Pay special attention to:
            - Serving sizes and units
            - Nutritional values and their units (g, mg, etc.)
            - Percentage daily values (% DV)
            - Ingredient names and order
            
            Return only the extracted text, no additional commentary.
            """
            
            response = self.gemini_model.generate_content([prompt, img])
            extracted_text = response.text.strip()
            
            print(f"[OCR] Gemini extracted {len(extracted_text)} characters")
            return {"text": extracted_text, "method": "Gemini Vision", "confidence": "very_high"}
            
        except Exception as e:
            print(f"[OCR] Gemini error: {e}")
            return {"error": str(e), "text": ""}
    
    def extract_with_google_vision(self, image_path: str) -> Dict[str, str]:
        """Extract text using Google Cloud Vision"""
        if not self.google_vision_client:
            return {"error": "Google Cloud Vision not available", "text": ""}
        
        try:
            print("[OCR] Using Google Cloud Vision...")
            
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.google_vision_client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            texts = response.text_annotations
            if texts:
                extracted_text = texts[0].description
                print(f"[OCR] Google Vision extracted {len(extracted_text)} characters")
                return {"text": extracted_text, "method": "Google Cloud Vision", "confidence": "high"}
            else:
                return {"text": "", "method": "Google Cloud Vision", "confidence": "low"}
                
        except Exception as e:
            print(f"[OCR] Google Cloud Vision error: {e}")
            return {"error": str(e), "text": ""}
    
    def extract_text_best_available(self, image_path: str) -> Dict[str, str]:
        """
        Extract text using the best available method
        Priority: Gemini Vision > Google Cloud Vision > EasyOCR > Fallback
        """
        # Preprocess image for better results
        processed_path = self.preprocess_image(image_path)
        
        # Try methods in order of preference
        methods = [
            ("Gemini Vision", self.extract_with_gemini),
            ("Google Cloud Vision", self.extract_with_google_vision),
            ("EasyOCR", self.extract_with_easyocr),
        ]
        
        for method_name, method_func in methods:
            try:
                result = method_func(processed_path)
                if result.get("text") and len(result["text"].strip()) > 10:
                    print(f"[OCR] Successfully extracted text using {method_name}")
                    return result
                else:
                    print(f"[OCR] {method_name} returned insufficient text")
            except Exception as e:
                print(f"[OCR] {method_name} failed: {e}")
                continue
        
        # Fallback to basic Tesseract if all else fails
        print("[OCR] Falling back to Tesseract...")
        try:
            import pytesseract
            from PIL import Image
            
            img = Image.open(processed_path)
            text = pytesseract.image_to_string(img, config='--psm 6')
            return {"text": text, "method": "Tesseract (fallback)", "confidence": "low"}
            
        except Exception as e:
            print(f"[OCR] All methods failed: {e}")
            return {"error": "All OCR methods failed", "text": ""}


# Global instance
enhanced_ocr = EnhancedOCR()

def extract_text_from_image(image_path: str) -> str:
    """
    Main function to extract text from nutrition label images
    Uses the best available OCR method automatically
    """
    result = enhanced_ocr.extract_text_best_available(image_path)
    
    if result.get("text"):
        print(f"[OCR] Extraction successful using {result.get('method', 'unknown')} method")
        print(f"[OCR] Confidence: {result.get('confidence', 'unknown')}")
        print(f"[OCR] Text preview: {result['text'][:200]}...")
        return result["text"]
    else:
        error_msg = result.get("error", "Unknown OCR error")
        print(f"[OCR] Extraction failed: {error_msg}")
        raise Exception(f"OCR extraction failed: {error_msg}")
