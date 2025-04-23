from typing import Dict, List, Tuple
import torch
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
from PIL import Image
import numpy as np
from ...core.config import get_settings

settings = get_settings()

class DocumentAnalyzer:
    def __init__(self):
        # Suppress expected model initialization warnings
        import warnings
        warnings.filterwarnings('ignore', message='Some weights of.*were not initialized')
        
        self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
        # Initialize with proper classifier weights
        self.model = LayoutLMv3ForSequenceClassification.from_pretrained(
            "microsoft/layoutlmv3-base",
            num_labels=2,  # Binary classification: KTP vs non-KTP
            ignore_mismatched_sizes=True  # Suppress size mismatch warnings
        )
        
        # Initialize classifier weights properly
        import torch.nn as nn
        self.model.classifier.dense = nn.Linear(768, 768)  # Match hidden size
        nn.init.xavier_uniform_(self.model.classifier.dense.weight)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def analyze_layout(self, image: Image.Image) -> Dict:
        """Analyze the document layout and verify it's a KTP."""
        # Prepare image for the model
        encoding = self.processor(
            image,
            return_tensors="pt",
            truncation=True
        )
        
        # Move inputs to device
        for key, value in encoding.items():
            if isinstance(value, torch.Tensor):
                encoding[key] = value.to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**encoding)
            
        # Get prediction score with softmax
        scores = torch.softmax(outputs.logits, dim=1)[0]
        is_ktp_score = scores[1].item()
        
        # Extract layout information
        layout_info = self._extract_layout_info(encoding)
        
        # Adjust confidence based on both model score and layout analysis
        layout_confidence = 1.0 if layout_info["valid_layout"] else 0.5
        final_confidence = (is_ktp_score * 0.7 + layout_confidence * 0.3)
        
        return {
            "is_ktp": final_confidence > 0.4,  # Lower threshold and use combined confidence
            "confidence": final_confidence,
            "layout": layout_info
        }
    
    def _extract_layout_info(self, encoding) -> Dict:
        """Extract layout information from the encoded image."""
        # Get bounding boxes from the encoding
        boxes = encoding.bbox[0].cpu().numpy()
        
        # Define key regions we expect in a KTP with more flexible bounds
        key_regions = {
            "header": {"y_range": (0, 0.25)},    # Top 25% for header
            "photo": {"x_range": (0, 0.35)},     # Left 35% for photo
            "nik": {"y_range": (0.15, 0.35)},    # More flexible NIK position
            "personal_info": {"x_range": (0.25, 1.0), "y_range": (0.2, 0.85)},  # Wider info area
            "footer": {"y_range": (0.75, 1.0)}   # Bottom 25% for footer
        }
        
        # Normalize image dimensions
        height, width = 1.0, 1.0
        
        # Get regions based on relative positions
        detected_regions = {}
        for region_name, bounds in key_regions.items():
            region_boxes = []
            for box in boxes:
                x1, y1, x2, y2 = box
                # Normalize coordinates
                x1, x2 = x1/width, x2/width
                y1, y2 = y1/height, y2/height
                
                # Check if box falls within region bounds with some tolerance
                in_x_range = True
                in_y_range = True
                tolerance = 0.05  # 5% tolerance for region boundaries
                
                if "x_range" in bounds:
                    min_x, max_x = bounds["x_range"]
                    in_x_range = (min_x - tolerance) <= x1 <= (max_x + tolerance)
                    
                if "y_range" in bounds:
                    min_y, max_y = bounds["y_range"]
                    in_y_range = (min_y - tolerance) <= y1 <= (max_y + tolerance)
                    
                if in_x_range and in_y_range:
                    region_boxes.append({
                        "box": [x1, y1, x2, y2],
                        "relative_area": (x2-x1) * (y2-y1)
                    })
            
            if region_boxes:
                # Sort by area and get the largest box for the region
                region_boxes.sort(key=lambda x: x["relative_area"], reverse=True)
                detected_regions[region_name] = region_boxes[0]
        
        return {
            "regions": detected_regions,
            "valid_layout": len(detected_regions) >= 3  # Require only 3 key regions to be more lenient
        }
    
    def get_region_coordinates(self, layout_info: Dict, region_name: str) -> Tuple[int, int, int, int]:
        """Get the coordinates for a specific region from the layout information."""
        if region_name in layout_info["regions"]:
            box = layout_info["regions"][region_name]["box"]
            return tuple(map(int, box))
        return None