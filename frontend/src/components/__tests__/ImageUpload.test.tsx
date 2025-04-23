import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ImageUpload from '../ImageUpload'

describe('ImageUpload', () => {
  it('renders upload area', () => {
    render(<ImageUpload onUpload={() => {}} />)
    expect(screen.getByText(/drag and drop.*ktp image/i)).toBeInTheDocument()
  })

  it('shows drag active state', async () => {
    render(<ImageUpload onUpload={() => {}} />)
    const dropzone = screen.getByTestId('dropzone')
    
    await act(async () => {
      fireEvent.dragEnter(dropzone, {
        dataTransfer: {
          items: [],
          types: ['Files']
        }
      })
    })

    // Wait for state update
    await new Promise(resolve => setTimeout(resolve, 0))
    
    const updatedDropzone = screen.getByTestId('dropzone')
    expect(updatedDropzone.className).toContain('border-blue-400')
    expect(updatedDropzone.className).toContain('bg-blue-50')
  })

  it('calls onUpload when file is dropped', async () => {
    const mockOnUpload = vi.fn()
    render(<ImageUpload onUpload={mockOnUpload} />)
    
    const file = new File(['dummy content'], 'ktp.jpg', { type: 'image/jpeg' })
    const dropzone = screen.getByTestId('dropzone')
    
    await act(async () => {
      const event = {
        dataTransfer: {
          files: [file],
          items: [
            {
              kind: 'file',
              type: file.type,
              getAsFile: () => file
            }
          ],
          types: ['Files']
        }
      }

      fireEvent.drop(dropzone, event)
    })
    
    expect(mockOnUpload).toHaveBeenCalledWith(file)
  })

  it('shows supported formats message', () => {
    render(<ImageUpload onUpload={() => {}} />)
    expect(screen.getByText(/supports jpg and png/i)).toBeInTheDocument()
  })
})