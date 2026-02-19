from PIL import Image
import pytesseract
import io
import base64
from typing import Optional, Dict, Any

class ImageAnalyzer:
    def __init__(self):
        # Configure tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze an image and extract text, objects, and other information.
        Returns a dictionary with analysis results.
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image, lang='fra+eng+ara')
            
            # Get image properties
            width, height = image.size
            format_type = image.format
            
            # Basic object detection (can be enhanced with ML models)
            analysis = {
                "text": extracted_text.strip(),
                "dimensions": {"width": width, "height": height},
                "format": format_type,
                "has_text": len(extracted_text.strip()) > 0,
                "description": self._generate_description(image)
            }
            
            return analysis
        except Exception as e:
            return {
                "error": str(e),
                "text": "",
                "has_text": False
            }

    def _generate_description(self, image: Image.Image) -> str:
        """
        Generate a basic description of the image.
        Can be enhanced with vision models like CLIP or GPT-4 Vision.
        """
        width, height = image.size
        
        # Basic description based on image properties
        if width > height:
            orientation = "paysage"
        elif height > width:
            orientation = "portrait"
        else:
            orientation = "carré"
        
        return f"Image {orientation} de {width}x{height} pixels"

    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extract text from image using OCR.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image, lang='fra+eng+ara')
            return text.strip()
        except Exception as e:
            return f"Erreur lors de l'extraction du texte: {str(e)}"

image_analyzer = ImageAnalyzer()
