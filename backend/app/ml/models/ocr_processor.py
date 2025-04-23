import pytesseract
from PIL import Image
import numpy as np
from ...core.config import get_settings
from typing import Dict, List, Tuple
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import torch

settings = get_settings()

class OCRProcessor:
    def __init__(self):
        self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
        self.model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def process_image(self, image: Image.Image) -> List[Dict[str, str]]:
        """Process an image and extract text with layout information."""
        # Prepare image for the model
        encoding = self.processor(
            image,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Move inputs to device
        for key, value in encoding.items():
            if isinstance(value, torch.Tensor):
                encoding[key] = value.to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**encoding)
            
        # Process outputs
        predictions = outputs.logits.argmax(-1).squeeze().tolist()
        token_boxes = encoding.bbox.squeeze().tolist()
        tokens = self.processor.tokenizer.convert_ids_to_tokens(encoding.input_ids.squeeze().tolist())
        
        # Group results
        results = []
        current_token = {"text": "", "box": None}
        
        for token, box, prediction in zip(tokens, token_boxes, predictions):
            if token.startswith("##"):
                # Continue previous token
                current_token["text"] += token[2:]
            else:
                # Add previous token if exists
                if current_token["text"] and current_token["box"]:
                    results.append(current_token)
                # Start new token
                current_token = {
                    "text": token,
                    "box": box
                }
        
        # Add final token
        if current_token["text"] and current_token["box"]:
            results.append(current_token)
        
        return results
    
    def get_field_candidates(self, text_boxes: List[Dict[str, str]], field_name: str) -> List[str]:
        """Get candidate values for a specific field based on layout and content."""
        # Field-specific rules for text selection
        field_rules = {
            "NIK": lambda text: text.isdigit() and len(text) == 16,
            "name": lambda text: text.isupper() and not any(char.isdigit() for char in text),
            "birthPlace": lambda text: text.isupper() and len(text) > 2,
            "birthDate": lambda text: any(char.isdigit() for char in text) and len(text) >= 8,
            "gender": lambda text: text in ["LAKI-LAKI", "PEREMPUAN"],
            "address": lambda text: len(text) > 10 and "RT" in text or "RW" in text
        }
        
        rule = field_rules.get(field_name, lambda _: True)
        return [box["text"] for box in text_boxes if rule(box["text"])]
    
    def extract_field(self, text_boxes: List[Dict[str, str]], field_name: str) -> str:
        """Extract specific field value from OCR results."""
        candidates = self.get_field_candidates(text_boxes, field_name)
        return candidates[0] if candidates else ""
    
    def extract_text(self, layout: dict) -> dict:
        """
        Extract text from the image regions identified by the document analyzer
        """
        text_regions = {}
        
        for region in layout['text_regions']:
            box = region['box']
            confidence = region['confidence']
            
            # Extract coordinates
            x1, y1, x2, y2 = [int(coord) for coord in box]
            
            # Get text from region
            text = self._extract_region_text(x1, y1, x2, y2)
            
            text_regions[f"region_{len(text_regions)}"] = {
                'text': text,
                'confidence': confidence,
                'box': box
            }
            
        return text_regions
    
    def _extract_region_text(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """
        Extract text from a specific region of the image
        """
        try:
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                np.array(self.current_image.crop((x1, y1, x2, y2))),
                config=self.config
            )
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from region: {str(e)}")
            return ""
            
    def preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Apply specific preprocessing steps for OCR optimization
        """
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
            
        # Apply additional preprocessing if needed
        # TODO: Add specific preprocessing steps for Indonesian KTP
        
        return image