from typing import Optional
import re
from datetime import datetime
from .enums import Gender, BloodType, Religion, MaritalStatus
from .errors import ValidationError

def validate_nik(nik: str, bypass_validation: bool = False) -> bool:
    """Validate Indonesian NIK (Nomor Induk Kependudukan)."""
    if bypass_validation:
        return True
        
    if not isinstance(nik, str) or len(nik) != 16:
        return False
    
    # Check if all characters are digits
    if not nik.isdigit():
        return False
    
    # Check province code (2 digits: 11-94)
    province = int(nik[:2])
    if province < 11 or province > 94:
        return False
    
    # Check regency/city code (2 digits: 01-99)
    regency = int(nik[2:4])
    if regency < 1 or regency > 99:
        return False
    
    # Check district code (2 digits: 01-99)
    district = int(nik[4:6])
    if district < 1 or district > 99:
        return False
    
    return True

def validate_name(name: str, bypass_validation: bool = False) -> bool:
    """Validate person name."""
    if bypass_validation:
        return True
        
    if not isinstance(name, str) or len(name) < 2:
        return False
    
    # Check if name is in uppercase
    if name != name.upper():
        return False
    
    # Allow letters, spaces, dots, apostrophes, commas, and hyphens
    pattern = r'^[A-Z\s\.\,\'\-]+$'
    return bool(re.match(pattern, name))

def validate_date(date_str: str, bypass_validation: bool = False) -> bool:
    """Validate date string in DD-MM-YYYY format."""
    if bypass_validation:
        return True
        
    if not isinstance(date_str, str):
        return False
    
    try:
        # Parse date string
        date = datetime.strptime(date_str, '%d-%m-%Y')
        
        # Check if year is reasonable (1900-current year)
        current_year = datetime.now().year
        if date.year < 1900 or date.year > current_year:
            return False
        
        return True
    except ValueError:
        return False

def validate_address(address: str, bypass_validation: bool = False) -> bool:
    """Validate address string."""
    if bypass_validation:
        return True
        
    if not isinstance(address, str) or len(address) < 5:
        return False
    
    # Check if address is in uppercase
    if address != address.upper():
        return False
    
    # Check for RT/RW pattern
    rt_rw_pattern = r'RT\.?\s*\d{1,3}(/|\.|\s+)RW\.?\s*\d{1,3}'
    return bool(re.search(rt_rw_pattern, address))

def validate_religion(religion: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate religion field."""
    if bypass_validation:
        return True
        
    if religion is None:  # Optional field
        return True
    
    valid_religions = {
        'ISLAM', 'KRISTEN', 'KATOLIK', 
        'HINDU', 'BUDDHA', 'KONGHUCU'
    }
    return religion in valid_religions

def validate_marital_status(status: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate marital status field."""
    if bypass_validation:
        return True
        
    if status is None:  # Optional field
        return True
    
    valid_statuses = {
        'BELUM KAWIN', 'KAWIN', 
        'CERAI HIDUP', 'CERAI MATI'
    }
    return status in valid_statuses

def validate_blood_type(blood_type: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate blood type field."""
    if bypass_validation:
        return True
        
    if blood_type is None:  # Optional field
        return True
    
    valid_types = {'A', 'B', 'AB', 'O', '-'}
    return blood_type in valid_types

def validate_gender(gender: str, bypass_validation: bool = False) -> bool:
    """Validate gender field."""
    if bypass_validation:
        return True
        
    if not isinstance(gender, str):
        return False
    
    valid_genders = {'LAKI-LAKI', 'PEREMPUAN'}
    return gender in valid_genders

def validate_nationality(nationality: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate nationality field."""
    if bypass_validation:
        return True
        
    if nationality is None:  # Optional field
        return True
    
    valid_nationalities = {'WNI', 'WNA'}
    return nationality in valid_nationalities

def validate_occupation(occupation: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate occupation field."""
    if bypass_validation:
        return True
        
    if occupation is None:  # Optional field
        return True
    
    # Occupation should be non-empty uppercase string
    if not isinstance(occupation, str) or len(occupation) < 1:
        return False
    
    return occupation == occupation.upper()

def validate_valid_until(valid_until: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate ID validity date."""
    if bypass_validation:
        return True
        
    if valid_until is None:  # Optional field
        return True
    
    if valid_until == 'SEUMUR HIDUP':
        return True
        
    try:
        # Parse date string
        date = datetime.strptime(valid_until, '%d-%m-%Y')
        
        # Check if date is in the future
        if date < datetime.now():
            return False
            
        return True
    except ValueError:
        return False

def validate_birth_place(birth_place: str, bypass_validation: bool = False) -> bool:
    """Validate birth place field."""
    if bypass_validation:
        return True
        
    if not isinstance(birth_place, str) or len(birth_place) < 2:
        return False
    
    # Birth place should be uppercase
    if birth_place != birth_place.upper():
        return False
    
    # Allow letters, spaces, and dots
    pattern = r'^[A-Z\s\.]+$'
    return bool(re.match(pattern, birth_place))

def validate_validity_date(date_str: Optional[str], bypass_validation: bool = False) -> bool:
    """Validate ID card validity date."""
    if bypass_validation:
        return True
        
    if date_str is None:  # Optional field
        return True
    
    if date_str == 'SEUMUR HIDUP':
        return True
    
    return validate_date(date_str, bypass_validation)