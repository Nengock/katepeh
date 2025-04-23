import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Loading from '../Loading'

describe('Loading', () => {
  it('renders loading message', () => {
    render(<Loading />)
    expect(screen.getByText(/processing ktp image/i)).toBeInTheDocument()
  })

  it('shows loading spinner', () => {
    render(<Loading />)
    const spinner = screen.getByTestId('loading-spinner')
    expect(spinner).toHaveClass('animate-spin')
  })
})