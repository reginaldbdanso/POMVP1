#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."

# Check if PostgreSQL is installed
if command -v pg_config >/dev/null 2>&1; then
    echo "PostgreSQL found, installing all dependencies..."
    pip install -r requirements.txt
else
    echo "PostgreSQL not found. Installing dependencies without psycopg2..."
    # Create a temporary requirements file without psycopg2
    grep -v psycopg2 requirements.txt > requirements_temp.txt
    pip install -r requirements_temp.txt
    
    # Install SQLite adapter instead
    pip install sqlalchemy
    
    # Set environment variable to use SQLite
    export DATABASE_URL="sqlite:///./test.db"
    
    echo "\nNOTE: PostgreSQL is not installed. Using SQLite as fallback."
    echo "For PostgreSQL support, install PostgreSQL and run:"
    echo "  brew install postgresql    # On macOS with Homebrew"
    echo "  sudo apt install postgresql postgresql-contrib libpq-dev    # On Ubuntu/Debian"
    echo "Then run this script again.\n"
    
    # Clean up temporary file
    rm requirements_temp.txt
fi

# Run the seed script
echo "Running database seed script..."
python seed_db.py

echo "Done! You can deactivate the virtual environment by typing 'deactivate'."