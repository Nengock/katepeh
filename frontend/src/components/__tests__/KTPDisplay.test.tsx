import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import KTPDisplay from '../KTPDisplay'
import { KTPData } from '@/types/ktp'

const mockKTPData: KTPData = {
  nik: "3173042504900001",
  name: "JOHN DOE",
  birth_place: "JAKARTA",
  birth_date: "1990-04-25",
  gender: "LAKI-LAKI",
  address: "JL. KEBON JERUK RT 001 RW 002 KEL. KEMANGGISAN KEC. PALMERAH",
  blood_type: "O",
  religion: "ISLAM",
  marital_status: "KAWIN",
  occupation: "KARYAWAN SWASTA",
  nationality: "WNI",
  valid_until: "SEUMUR HIDUP"
}

describe('KTPDisplay', () => {
  it('displays KTP data correctly', () => {
    render(<KTPDisplay data={mockKTPData} onReset={() => {}} />)
    
    expect(screen.getByText(mockKTPData.name)).toBeInTheDocument()
    expect(screen.getByText(mockKTPData.nik)).toBeInTheDocument()
    expect(screen.getByText(mockKTPData.address)).toBeInTheDocument()
  })

  it('calls onReset when reset button is clicked', () => {
    const mockReset = vi.fn()
    render(<KTPDisplay data={mockKTPData} onReset={mockReset} />)
    
    const resetButton = screen.getByText(/proses ktp lain/i)
    fireEvent.click(resetButton)
    
    expect(mockReset).toHaveBeenCalled()
  })

  it('shows field labels in Indonesian', () => {
    render(<KTPDisplay data={mockKTPData} onReset={() => {}} />)
    
    const labels = [
      'NIK',
      'Nama',
      'Tempat Lahir',
      'Tanggal Lahir',
      'Jenis Kelamin',
      'Alamat',
      'Golongan Darah',
      'Agama',
      'Status Perkawinan'
    ]
    
    labels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument()
    })
  })

  it('handles optional fields correctly', () => {
    const partialData = {
      nik: "3173042504900001",
      name: "JOHN DOE",
      birth_place: "JAKARTA",
      birth_date: "1990-04-25",
      gender: "LAKI-LAKI",
      address: "JL. KEBON JERUK"
    }
    
    render(<KTPDisplay data={partialData as KTPData} onReset={() => {}} />)
    
    // Optional fields should not be displayed if not present
    expect(screen.queryByText('Golongan Darah')).not.toBeInTheDocument()
    expect(screen.queryByText('Agama')).not.toBeInTheDocument()
  })
})