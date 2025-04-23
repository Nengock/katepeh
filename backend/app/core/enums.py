from enum import Enum

class Gender(str, Enum):
    MALE = "LAKI-LAKI"
    FEMALE = "PEREMPUAN"

class BloodType(str, Enum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    UNKNOWN = "-"

class Religion(str, Enum):
    ISLAM = "ISLAM"
    KRISTEN = "KRISTEN"
    KATOLIK = "KATOLIK"
    HINDU = "HINDU"
    BUDDHA = "BUDDHA"
    KONGHUCU = "KONGHUCU"
    OTHER = "OTHER"

class MaritalStatus(str, Enum):
    SINGLE = "BELUM KAWIN"
    MARRIED = "KAWIN"
    DIVORCED = "CERAI HIDUP"
    WIDOWED = "CERAI MATI"