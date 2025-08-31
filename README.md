# Qode Project

A full-stack application with a React/TypeScript frontend and Python FastAPI backend.

## Project Structure

```
qode/
├── frontend/               # React + TypeScript + Vite frontend
│   ├── src/               # Frontend source code
│   ├── public/            # Static assets
│   ├── Dockerfile         # Frontend Docker configuration
│   └── nginx.conf         # Nginx configuration for serving frontend
│
├── backend/               # Python FastAPI backend
│   └── qode-intel/
│       ├── app/          # Backend application code
│       │   ├── api/      # API routes
│       │   ├── models/   # Data models
│       │   ├── services/ # Business logic
│       │   └── utils/    # Utility functions
│       ├── data/         # Data storage
│       ├── tests/        # Backend tests
│       └── Dockerfile    # Backend Docker configuration
│
└── docker-compose.yml    # Docker composition configuration
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- pnpm (for frontend package management)

## Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd qode
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the applications:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development Setup

### Frontend (React + TypeScript + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Start the development server:
   ```bash
   pnpm dev
   ```

The frontend will be available at http://localhost:5173

### Backend (FastAPI + Python)

1. Navigate to the backend directory:
   ```bash
   cd backend/qode-intel
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

The backend API will be available at http://localhost:8000

## API Documentation

- OpenAPI documentation is available at http://localhost:8000/docs
- ReDoc alternative documentation at http://localhost:8000/redoc

## Project Features

### Frontend
- React with TypeScript for type-safe development
- Vite for fast development and optimized builds
- Modern UI with responsive design
- Component-based architecture

### Backend
- FastAPI for high-performance API development
- Playwright integration for web scraping capabilities
- Data processing and analysis features
- Modular service architecture

## Data Storage

The backend uses a file-based storage system with the following structure:
- `/data/raw/`: Raw scraped data
- `/data/processed/`: Processed and analyzed data
- `/data/parquet/`: Data stored in Parquet format

## Docker Configuration

The project uses Docker for containerization with the following setup:

### Frontend Container
- Base image: Node.js 18 Alpine for build, Nginx Alpine for serving
- Exposed port: 5173
- Optimized multi-stage build process
- Nginx configuration for SPA routing

### Backend Container
- Base image: Python with Playwright
- Exposed port: 8000
- Volume mounting for persistent data storage
- Environment variable support

## Development Guidelines

1. Code Style
   - Frontend: Follow TypeScript best practices
   - Backend: Follow PEP 8 guidelines
   - Use meaningful variable and function names

2. Testing
   - Write unit tests for new features
   - Run tests before committing changes

3. Version Control
   - Use feature branches
   - Write meaningful commit messages
   - Review code before merging

## Troubleshooting

Common issues and solutions:

1. Docker Build Issues
   - Ensure Docker daemon is running
   - Check for conflicting ports
   - Verify Docker resource allocation

2. Frontend Development
   - Clear node_modules and reinstall if facing dependency issues
   - Check for proper environment variable configuration

3. Backend Development
   - Verify Python version compatibility
   - Check virtual environment activation
   - Ensure all required dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

[Add your license information here]
