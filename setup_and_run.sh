#!/bin/bash

# Exit on error
set -e

# # Create virtual environment if it doesn't exist
# if [ ! -d "venv" ]; then
#     echo "Creating virtual environment..."
#     python3 -m venv venv
# else
#     echo "Virtual environment already exists."
# fi

# # Activate virtual environment
# echo "Activating virtual environment..."
# source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."

# Check if MySQL is installed
if command -v mysql >/dev/null 2>&1; then
    echo "MySQL found, installing all dependencies..."
    pip install -r requirements.txt
else
    echo "MySQL not found. Installing dependencies without mysqlclient..."
    # Create a temporary requirements file without mysqlclient
    grep -v mysqlclient requirements.txt > requirements_temp.txt
    pip install -r requirements_temp.txt
    
    # Install SQLite adapter instead
    pip install sqlalchemy
    
    # Set environment variable to use SQLite
    export DATABASE_URL="sqlite:///./test.db"
    
    echo "\nNOTE: MySQL is not installed. Using SQLite as fallback."
    echo "For MySQL support, install MySQL and run:"
    echo "  winget install MySQL.MySQL    # On Windows"
    echo "  brew install mysql    # On macOS with Homebrew"
    echo "  sudo apt install mysql-server mysql-client libmysqlclient-dev    # On Ubuntu/Debian"
    echo "Then run this script again.\n"
    
    # Clean up temporary file
    rm requirements_temp.txt
fi

# Run the seed script
echo "Running database seed script..."
python seed_db.py

echo "Done! You can deactivate the virtual environment by typing 'deactivate'."