# Indonesian KTP Recognition System

This project provides a web-based system for extracting information from Indonesian ID cards (KTP) using machine learning and OCR technology.

## Features

- Upload KTP images through drag-and-drop or file selection
- Automatic text extraction and information parsing
- Structured data output with confidence scores
- Modern, responsive user interface
- Support for both JPEG and PNG formats

## Tech Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- React Dropzone for file uploads
- Axios for API communication

### Backend
- FastAPI
- PyTorch for ML models
- Transformers (LayoutLMv3) for document layout analysis
- Tesseract OCR for text extraction
- OpenCV for image preprocessing

## Setup

### Backend Setup

1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

- `POST /api/upload`: Upload a KTP image
- `POST /api/extract`: Extract information from a KTP image
- `GET /api/export/{format}`: Export extracted data in various formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License