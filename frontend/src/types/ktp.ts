export type Gender = 'LAKI-LAKI' | 'PEREMPUAN'
export type BloodType = 'A' | 'B' | 'AB' | 'O' | '-'

export interface KTPData {
  nik: string
  name: string
  birth_place: string
  birth_date: string
  gender: Gender
  address: string
  blood_type?: BloodType
  religion?: string
  marital_status?: string
  occupation?: string
  nationality?: string
  valid_until?: string
}