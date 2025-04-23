from pydantic import BaseModel, Field, field_validator
from typing import Optional, ClassVar
from datetime import date
import re
from .enums import Gender, BloodType, Religion, MaritalStatus
from .validators import (
    validate_nik, validate_name, validate_date,
    validate_birth_place, validate_address, validate_religion,
    validate_marital_status, validate_blood_type, validate_gender,
    validate_nationality, validate_occupation, validate_valid_until
)
from .validators import validate_nik, validate_name, validate_date
from .validators import validate_birth_place, validate_address  
class KTPData(BaseModel):
    nik: str = Field(..., description="16-digit National ID Number")
    name: str = Field(..., description="Full name as appears on ID")
    birth_place: str = Field(..., description="Place of birth")
    birth_date: str = Field(..., description="Date of birth (DD-MM-YYYY)")
    gender: Optional[str] = Field(None, description="Gender (e.g., LAKI-LAKI or PEREMPUAN)")
    address: str = Field(..., description="Full residential address")
    blood_type: Optional[BloodType] = Field(None, description="Blood type if present")
    religion: Optional[Religion] = Field(None, description="Religion")
    marital_status: Optional[MaritalStatus] = Field(None, description="Marital status")
    occupation: Optional[str] = Field(None, description="Occupation/profession")
    nationality: Optional[str] = Field(None, description="Nationality (default: WNI)")
    valid_until: Optional[str] = Field(None, description="ID validity date or SEUMUR HIDUP")

    model_config = {
        "bypass_validation": True
    }

    @field_validator('nik')
    def validate_nik_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_nik(v, bypass):
            raise ValueError('NIK must be exactly 16 digits')
        return v

    @field_validator('name')
    def validate_name_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_name(v, bypass):
            raise ValueError('Name must contain only uppercase letters, spaces, and allowed punctuation')
        return v

    @field_validator('birth_place')
    def validate_birth_place_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_birth_place(v, bypass):
            raise ValueError('Birth place must be in uppercase letters')
        return v

    @field_validator('birth_date')
    def validate_birth_date_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_date(v, bypass):
            raise ValueError('Birth date must be in DD-MM-YYYY format')
        return v

    @field_validator('address')
    def validate_address_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_address(v, bypass):
            raise ValueError('Address must be in uppercase and contain RT/RW information')
        return v

    @field_validator('religion')
    def validate_religion_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if v and not validate_religion(v, bypass):
            raise ValueError('Invalid religion value')
        return v

    @field_validator('marital_status')
    def validate_marital_status_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if v and not validate_marital_status(v, bypass):
            raise ValueError('Invalid marital status')
        return v

    @field_validator('blood_type')
    def validate_blood_type_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if v and not validate_blood_type(v, bypass):
            raise ValueError('Invalid blood type')
        return v

    @field_validator('gender')
    def validate_gender_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if not validate_gender(v, bypass):
            raise ValueError('Gender must be either LAKI-LAKI or PEREMPUAN')
        return v

    @field_validator('nationality')
    def validate_nationality_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        v = v or 'WNI'
        if not validate_nationality(v, bypass):
            raise ValueError('Nationality must be either WNI or WNA')
        return v

    @field_validator('occupation')
    def validate_occupation_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if v and not validate_occupation(v, bypass):
            raise ValueError('Occupation must be in uppercase letters')
        return v

    @field_validator('valid_until')
    def validate_valid_until_field(cls, v):
        bypass = cls.model_config.get("bypass_validation", True)
        if v and not validate_valid_until(v, bypass):
            raise ValueError('Valid until must be either SEUMUR HIDUP or a future date in DD-MM-YYYY format')
        return v

class ImageUploadResponse(BaseModel):
    success: bool = Field(..., description="Whether the upload was successful")
    message: str = Field(..., description="Status message")
    file_id: Optional[str] = Field(None, description="ID of the uploaded file")

class ExtractionResponse(BaseModel):
    ktp_data: KTPData = Field(..., description="Extracted KTP data")
    confidence_score: float = Field(
        ...,
        description="Confidence score of the extraction (0-1)",
        ge=0,
        le=1
    )