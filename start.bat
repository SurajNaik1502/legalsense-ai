@echo off
echo 🚀 LegalSense AI - Quick Start
echo ================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo # OpenAI API Configuration ^(optional but recommended^)
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Server Configuration
        echo HOST=0.0.0.0
        echo PORT=8000
        echo DEBUG=true
        echo.
        echo # File Upload Configuration
        echo MAX_FILE_SIZE=10485760
        echo UPLOAD_DIR=uploads
        echo PROCESSED_DIR=processed
    ) > .env
    echo ✅ Created .env file. Please edit it with your OpenAI API key if you have one.
)

echo 🔧 Building and starting services...
docker-compose up --build -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if services are running
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend failed to start. Check logs with: docker-compose logs backend
) else (
    echo ✅ Backend is running at http://localhost:8000
)

curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend failed to start. Check logs with: docker-compose logs frontend
) else (
    echo ✅ Frontend is running at http://localhost:3000
)

echo.
echo 🎉 LegalSense AI is starting up!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 📋 Useful commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo.
echo 🔍 Check the README.md for detailed usage instructions.
pause

