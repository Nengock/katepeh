from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from PIL import Image
import io
from ..core.models import KTPData, ImageUploadResponse, ExtractionResponse
from ..ml.models.document_analyzer import DocumentAnalyzer
from ..ml.models.ocr_processor import OCRProcessor
from ..ml.models.information_extractor import InformationExtractor
from ..ml.preprocessors.image_preprocessor import ImagePreprocessor
from ..core.config import get_settings
from ..core.errors import KTPProcessingError, ValidationError

router = APIRouter()
settings = get_settings()

# Initialize ML models
document_analyzer = DocumentAnalyzer()
ocr_processor = OCRProcessor()
info_extractor = InformationExtractor()
image_preprocessor = ImagePreprocessor()

@router.post("/upload", response_model=KTPData)
async def process_ktp(
    file: UploadFile = File(...),
    bypass_validation: bool = Query(True, description="Whether to bypass validation checks")
):
    """Process uploaded KTP image and extract information."""
    try:
        # Validate file type (skip if bypassing validation)
        if not bypass_validation and not file.content_type in ["image/jpeg", "image/png"]:
            raise ValidationError(
                f"Unsupported file type: {file.content_type}. Only JPEG and PNG images are supported"
            )
            
        # Read and validate file content
        try:
            contents = await file.read()
            if not contents:
                raise ValidationError("Empty file uploaded")
            image = Image.open(io.BytesIO(contents))
        except Exception as e:
            raise ValidationError(f"Invalid image file: {str(e)}")
        
        try:
            # Preprocess image with bypass_validation setting
            preprocessed_image = image_preprocessor.preprocess(image, bypass_validation=bypass_validation)
        except Exception as e:
            raise ValidationError(f"Image preprocessing failed: {str(e)}")
            
        # Analyze document layout
        try:
            layout_info = document_analyzer.analyze_layout(preprocessed_image)
            if not bypass_validation and not layout_info["is_ktp"]:
                raise ValidationError(
                    "The uploaded image does not appear to be a valid KTP. " +
                    f"Confidence score: {layout_info['confidence']:.2f}"
                )
        except Exception as e:
            raise ValidationError(f"Document analysis failed: {str(e)}")
            
        # Extract text from regions
        try:
            text_regions = ocr_processor.process_image(preprocessed_image)
            if not text_regions and not bypass_validation:
                raise ValidationError("No text could be extracted from the image")
        except Exception as e:
            raise ValidationError(f"OCR processing failed: {str(e)}")
        
        # Extract structured information
        try:
            ktp_data = info_extractor.extract_information(text_regions)
            if not ktp_data and not bypass_validation:
                raise ValidationError("Could not extract KTP information from the image")
        except Exception as e:
            raise ValidationError(f"Information extraction failed: {str(e)}")
        
        # Create and validate KTPData model with bypass_validation flag
        try:
            return KTPData(bypass_validation=bypass_validation, **ktp_data)
        except Exception as e:
            raise ValidationError(f"Invalid KTP data format: {str(e)}")
        
    except ValidationError as e:
        raise HTTPException(
            status_code=422, 
            detail={"error": str(e)}
        )
    except KTPProcessingError as e:
        raise HTTPException(
            status_code=500, 
            detail={"error": str(e), "type": "processing_error"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "An unexpected error occurred while processing the image", "details": str(e)}
        )

@router.post("/extract", response_model=ExtractionResponse)
async def extract_information(
    file: UploadFile,
    bypass_validation: bool = Query(False, description="Whether to bypass validation checks")
):
    """Extract information from a KTP image."""
    try:
        # Read file contents
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Preprocess image
        preprocessed_image = image_preprocessor.preprocess(image, bypass_validation=bypass_validation)
        
        # Analyze document layout
        layout_info = document_analyzer.analyze_layout(preprocessed_image)
        if not bypass_validation and not layout_info["is_ktp"]:
            raise ValidationError(
                "The uploaded image does not appear to be a valid KTP. " +
                f"Confidence score: {layout_info['confidence']:.2f}"
            )
            
        # Extract text from image
        text_regions = ocr_processor.process_image(preprocessed_image)
        if not text_regions and not bypass_validation:
            raise ValidationError("No text could be extracted from the image")
            
        # Extract structured information
        extracted_info = info_extractor.extract_information(text_regions)
        if not extracted_info and not bypass_validation:
            raise ValidationError("Could not extract KTP information from the image")
            
        # Calculate confidence score based on layout and extraction results
        confidence_score = layout_info["confidence"]
        
        # Create KTP data model
        ktp_data = KTPData(bypass_validation=bypass_validation, **extracted_info)
        
        return ExtractionResponse(
            ktp_data=ktp_data,
            confidence_score=confidence_score
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Failed to process image: {str(e)}"}
        )

@router.get("/export/{format}")
async def export_data(format: str, ktp_data: KTPData):
    if format not in ["json", "csv"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported export format. Use 'json' or 'csv'"
        )
    
    # Implementation for export functionality
    # Will be implemented based on format requirements

@router.get("/health")
async def health_check():
    """Check if all ML models are loaded and ready."""
    try:
        # Verify models are loaded
        models_status = {
            "document_analyzer": document_analyzer is not None,
            "ocr_processor": ocr_processor is not None,
            "info_extractor": info_extractor is not None
        }
        
        if all(models_status.values()):
            return {"status": "healthy", "models": models_status}
            
        return {
            "status": "degraded",
            "models": models_status,
            "message": "Some models are not loaded"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }