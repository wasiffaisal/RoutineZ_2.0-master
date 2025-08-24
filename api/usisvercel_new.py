# This file imports from the modularized code to maintain backward compatibility
# It serves as a bridge between the old monolithic structure and the new modular structure

from routinez.main import app

# This allows the existing code to continue working while using the new modular structure
if __name__ == "__main__":
    app.run()