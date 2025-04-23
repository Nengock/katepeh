import pytest
from datetime import datetime, timedelta
from app.core.validators import (
    validate_nik, validate_name, validate_date,
    validate_address, validate_religion, validate_marital_status,
    validate_blood_type, validate_gender, validate_nationality,
    validate_validity_date, validate_occupation, validate_valid_until,
    validate_birth_place
)

def test_validate_nik():
    # Valid NIKs
    assert validate_nik("3171234567890123")
    assert validate_nik("3275012304560001")
    
    # Invalid NIKs
    assert not validate_nik("123")  # Too short
    assert not validate_nik("abcdefghijklmnop")  # Non-numeric
    assert not validate_nik("0071234567890123")  # Invalid province code
    assert not validate_nik("3100234567890123")  # Invalid regency code
    assert not validate_nik("3175004567890123")  # Invalid district code

def test_validate_name():
    # Valid names
    assert validate_name("JOHN DOE")
    assert validate_name("MARY JANE O'CONNOR")
    assert validate_name("ABDUL AL-RAHMAN")
    
    # Invalid names
    assert not validate_name("john doe")  # Lowercase
    assert not validate_name("J")  # Too short
    assert not validate_name("JOHN123")  # Contains numbers
    assert not validate_name("")  # Empty string

def test_validate_date():
    # Valid dates
    assert validate_date("01-01-2000")
    assert validate_date("31-12-1999")
    assert validate_date("29-02-2020")  # Leap year
    
    # Invalid dates
    assert not validate_date("2000-01-01")  # Wrong format
    assert not validate_date("32-01-2000")  # Invalid day
    assert not validate_date("29-02-2021")  # Not a leap year
    assert not validate_date("01-13-2000")  # Invalid month
    assert not validate_date("01-01-1800")  # Year too early

def test_validate_address():
    # Valid addresses
    assert validate_address("JL. MERDEKA NO. 17 RT.001/RW.002")
    assert validate_address("DESA SUKAMAJU RT 05 RW 02")
    assert validate_address("KOMP. GRIYA INDAH BLOK A2 RT.010/RW.005")
    
    # Invalid addresses
    assert not validate_address("jalan merdeka")  # Lowercase
    assert not validate_address("JL. MERDEKA")  # No RT/RW
    assert not validate_address("")  # Empty string
    assert not validate_address("RT")  # Too short

def test_validate_religion():
    # Valid religions
    assert validate_religion("ISLAM")
    assert validate_religion("KRISTEN")
    assert validate_religion("KATOLIK")
    assert validate_religion("HINDU")
    assert validate_religion("BUDDHA")
    assert validate_religion("KONGHUCU")
    assert validate_religion(None)  # Optional field
    
    # Invalid religions
    assert not validate_religion("ANOTHER")
    assert not validate_religion("Islam")  # Case sensitive
    assert not validate_religion("")

def test_validate_marital_status():
    # Valid statuses
    assert validate_marital_status("BELUM KAWIN")
    assert validate_marital_status("KAWIN")
    assert validate_marital_status("CERAI HIDUP")
    assert validate_marital_status("CERAI MATI")
    assert validate_marital_status(None)  # Optional field
    
    # Invalid statuses
    assert not validate_marital_status("SINGLE")
    assert not validate_marital_status("Kawin")  # Case sensitive
    assert not validate_marital_status("")

def test_validate_blood_type():
    # Valid blood types
    assert validate_blood_type("A")
    assert validate_blood_type("B")
    assert validate_blood_type("AB")
    assert validate_blood_type("O")
    assert validate_blood_type("-")
    assert validate_blood_type(None)  # Optional field
    
    # Invalid blood types
    assert not validate_blood_type("C")
    assert not validate_blood_type("a")  # Case sensitive
    assert not validate_blood_type("")

def test_validate_gender():
    assert validate_gender("LAKI-LAKI") is True
    assert validate_gender("PEREMPUAN") is True
    assert validate_gender("MALE") is False
    assert validate_gender("") is False
    assert validate_gender(None) is False

def test_validate_nationality():
    assert validate_nationality("WNI") is True
    assert validate_nationality("WNA") is True
    assert validate_nationality(None) is True  # Optional field
    assert validate_nationality("INDO") is False
    assert validate_nationality("") is False

def test_validate_occupation():
    assert validate_occupation("WIRASWASTA") is True
    assert validate_occupation("PEGAWAI NEGERI") is True
    assert validate_occupation(None) is True  # Optional field
    assert validate_occupation("") is False
    assert validate_occupation("Engineer") is False  # Not uppercase

def test_validate_valid_until():
    # Test SEUMUR HIDUP case
    assert validate_valid_until("SEUMUR HIDUP") is True
    
    # Test valid future date
    future_date = (datetime.now() + timedelta(days=365)).strftime('%d-%m-%Y')
    assert validate_valid_until(future_date) is True
    
    # Test invalid past date
    past_date = (datetime.now() - timedelta(days=365)).strftime('%d-%m-%Y')
    assert validate_valid_until(past_date) is False
    
    # Test invalid format
    assert validate_valid_until("2025/12/31") is False
    assert validate_valid_until("") is False
    assert validate_valid_until(None) is True  # Optional field

def test_validate_birth_place():
    assert validate_birth_place("JAKARTA") is True
    assert validate_birth_place("BANDUNG BARAT") is True
    assert validate_birth_place("KAB. BOGOR") is True
    assert validate_birth_place("jakarta") is False  # Must be uppercase
    assert validate_birth_place("JAKARTA123") is False  # No numbers allowed
    assert validate_birth_place("") is False
    assert validate_birth_place("A") is False  # Too short

def test_validate_nationality():
    # Valid nationalities
    assert validate_nationality("WNI")
    assert validate_nationality("WNA")
    assert validate_nationality(None)  # Optional field
    
    # Invalid nationalities
    assert not validate_nationality("INDONESIAN")
    assert not validate_nationality("wni")  # Case sensitive
    assert not validate_nationality("")

def test_validate_validity_date():
    # Valid dates
    assert validate_validity_date("01-01-2025")
    assert validate_validity_date("SEUMUR HIDUP")
    assert validate_validity_date(None)  # Optional field
    
    # Invalid dates
    assert not validate_validity_date("2025-01-01")  # Wrong format
    assert not validate_validity_date("32-01-2025")  # Invalid day
    assert not validate_validity_date("")
    assert not validate_validity_date("seumur hidup")  # Case sensitive