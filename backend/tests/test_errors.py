import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.errors import ValidationError, OCRError, ModelError
from app.core.errors import (
    KTPProcessingError,
    ValidationError,
    OCRError,
    ModelError,
    DocumentError,
    PreprocessingError
)

client = TestClient(app)

def test_validation_error():
    @app.get("/test/validation-error")
    def validation_error_route():
        raise ValidationError("Invalid KTP data")

    response = client.get("/test/validation-error")
    assert response.status_code == 422
    assert response.json() == {"error": "Invalid KTP data"}

def test_ocr_error():
    @app.get("/test/ocr-error")
    def ocr_error_route():
        raise OCRError("Failed to process image")

    response = client.get("/test/ocr-error")
    assert response.status_code == 500
    assert response.json() == {"error": "Failed to process image"}

def test_model_error():
    @app.get("/test/model-error")
    def model_error_route():
        raise ModelError("Model prediction failed")

    response = client.get("/test/model-error")
    assert response.status_code == 500
    assert response.json() == {"error": "Model prediction failed"}

def test_unexpected_error():
    @app.get("/test/unexpected-error")
    def unexpected_error_route():
        raise RuntimeError("Something went wrong")

    response = client.get("/test/unexpected-error")
    assert response.status_code == 500
    assert response.json() == {"error": "An unexpected error occurred"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ktp_processing_error():
    error = KTPProcessingError("Test error", status_code=500, details={"field": "value"})
    assert str(error) == "Test error"
    assert error.status_code == 500
    assert error.details == {"field": "value"}

def test_validation_error():
    error = ValidationError("Invalid input", details={"field": "required"})
    assert str(error) == "Invalid input"
    assert error.status_code == 422
    assert error.details == {"field": "required"}

def test_ocr_error():
    error = OCRError("OCR failed", details={"confidence": 0.5})
    assert str(error) == "OCR failed"
    assert error.status_code == 500
    assert error.details == {"confidence": 0.5}

def test_model_error():
    error = ModelError("Model prediction failed")
    assert str(error) == "Model prediction failed"
    assert error.status_code == 500
    assert error.details == {}

def test_document_error():
    error = DocumentError("Invalid document type")
    assert str(error) == "Invalid document type"
    assert error.status_code == 400
    assert error.details == {}

def test_preprocessing_error():
    error = PreprocessingError("Image preprocessing failed")
    assert str(error) == "Image preprocessing failed"
    assert error.status_code == 400
    assert error.details == {}