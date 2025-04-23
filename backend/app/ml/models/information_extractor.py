from typing import Dict, List
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import re
from datetime import datetime
from ...core.models import KTPData, Gender, BloodType
from ...core.config import get_settings
from ...core.validators import (
    validate_nik, validate_name, validate_date,
    validate_address, validate_religion, validate_marital_status
)
from ...core.errors import KTPProcessingError

settings = get_settings()

class InformationExtractor:
    def __init__(self):
        # Suppress expected model initialization warnings
        import warnings
        warnings.filterwarnings('ignore', message='Some weights of.*were not initialized')
        
        self.tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")
        # Initialize with proper token classification weights
        self.model = AutoModelForTokenClassification.from_pretrained(
            "indolem/indobert-base-uncased",
            num_labels=13,  # Number of KTP fields we're extracting
            ignore_mismatched_sizes=True
        )
        
        # Initialize classifier weights properly
        import torch.nn as nn
        self.model.classifier = nn.Linear(768, 13)  # Match BERT hidden size to num_labels
        nn.init.xavier_uniform_(self.model.classifier.weight)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Field labels mapping
        self.label2field = {
            0: "nik",
            1: "name",
            2: "birth_place",
            3: "birth_date",
            4: "gender",
            5: "blood_type",
            6: "address",
            7: "rt_rw",
            8: "village",
            9: "district",
            10: "religion",
            11: "marital_status",
            12: "occupation"
        }
    
    def extract_information(self, text_regions: List[Dict[str, str]]) -> Dict[str, str]:
        """Extract structured information from OCR text regions."""
        extracted_info = {}
        
        # Combine all text for processing
        full_text = " ".join([region["text"] for region in text_regions])
        
        # Tokenize text
        inputs = self.tokenizer(
            full_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        ).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
        
        # Convert token predictions to field values
        tokens = self.tokenizer.convert_ids_to_tokens(inputs.input_ids.squeeze().tolist())
        current_field = None
        current_value = []
        
        for token, pred in zip(tokens, predictions):
            if pred in self.label2field:
                if current_field and current_value:
                    # Process and add previous field
                    extracted_info[current_field] = self._process_field_value(
                        current_field,
                        "".join(current_value).strip()
                    )
                current_field = self.label2field[pred]
                current_value = []
            elif token not in ["[CLS]", "[SEP]", "[PAD]"]:
                if current_field:
                    # Continue building current field value
                    if token.startswith("##"):
                        current_value.append(token[2:])
                    else:
                        current_value.append(" " + token if current_value else token)
        
        # Add last field if exists
        if current_field and current_value:
            extracted_info[current_field] = self._process_field_value(
                current_field,
                "".join(current_value).strip()
            )
        
        # Post-process specific fields
        self._post_process_fields(extracted_info)
        
        return extracted_info
    
    def _process_field_value(self, field: str, value: str) -> str:
        """Process extracted field value based on field type."""
        value = value.strip()
        
        if field == "nik":
            # Extract only digits
            return "".join(filter(str.isdigit, value))
        elif field in ["birth_place", "name", "religion", "occupation"]:
            # Convert to uppercase and remove extra spaces
            return " ".join(value.upper().split())
        elif field == "birth_date":
            # Try to parse and format date
            try:
                # Handle various date formats
                date_patterns = [
                    r"(\d{2})-(\d{2})-(\d{4})",
                    r"(\d{2})/(\d{2})/(\d{4})",
                    r"(\d{2})-(\d{2})-(\d{2})"
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, value)
                    if match:
                        day, month, year = match.groups()
                        if len(year) == 2:
                            year = "19" + year if int(year) > 50 else "20" + year
                        return f"{day}-{month}-{year}"
            except:
                pass
            return value
        elif field == "address":
            # Combine address components
            address_parts = []
            for part in value.split():
                if part.strip():
                    if part.startswith("RT") or part.startswith("RW"):
                        address_parts.append(part)
                    else:
                        address_parts.append(part.upper())
            return " ".join(address_parts)
        
        return value
    
    def _post_process_fields(self, extracted_info: Dict[str, str]):
        """Apply post-processing rules to extracted fields."""
        # Combine address components if separated
        address_components = []
        if "address" in extracted_info:
            address_components.append(extracted_info["address"])
        if "rt_rw" in extracted_info:
            address_components.append(extracted_info["rt_rw"])
        if "village" in extracted_info:
            address_components.append(f"KEL. {extracted_info['village']}")
        if "district" in extracted_info:
            address_components.append(f"KEC. {extracted_info['district']}")
        
        if address_components:
            extracted_info["address"] = " ".join(address_components)
            
        # Clean up temporary fields
        for field in ["rt_rw", "village", "district"]:
            extracted_info.pop(field, None)
        
        # Ensure required fields exist
        required_fields = ["nik", "name", "birth_place", "birth_date", "gender", "address"]
        for field in required_fields:
            if field not in extracted_info:
                extracted_info[field] = ""