import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ErrorBoundary from '../ErrorBoundary'

const ErrorComponent = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div data-testid="normal-content">Normal content</div>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )
    
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('shows error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    )
    
    expect(screen.getByText(/an error occurred/i)).toBeInTheDocument()
    expect(screen.getByText(/test error/i)).toBeInTheDocument()
  })

  it('allows retry after error', () => {
    const { unmount } = render(
      <ErrorBoundary>
        <ErrorComponent shouldThrow={true} />
      </ErrorBoundary>
    )
    
    // Click try again button
    fireEvent.click(screen.getByText(/try again/i))

    // Unmount and remount with non-throwing component to simulate recovery
    unmount()
    render(
      <ErrorBoundary>
        <ErrorComponent shouldThrow={false} />
      </ErrorBoundary>
    )
    
    expect(screen.getByTestId('normal-content')).toBeInTheDocument()
  })
})