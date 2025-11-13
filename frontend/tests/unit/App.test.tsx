import { render, screen } from '@testing-library/react'
import App from '@/App'

describe('App', () => {
  it('renders the app title', () => {
    render(<App />)
    expect(screen.getByText(/社群留言爬取工具/i)).toBeInTheDocument()
  })

  it('shows development message', () => {
    render(<App />)
    expect(screen.getByText(/正在開發中/i)).toBeInTheDocument()
  })
})
