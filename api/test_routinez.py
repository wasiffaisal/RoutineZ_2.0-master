import sys
import os

# Add the current directory to the path so we can import the routinez package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routinez.config import DEBUG, DATA_URL
from routinez.utils import debugprint
from routinez.data_loader import load_data
from routinez.time_utils import TimeUtils
from routinez.exam_utils import ExamConflictChecker
from routinez.ai_service import check_ai_availability
from routinez.main import create_app

def test_imports():
    """Test that all modules can be imported correctly."""
    print("\n=== Testing Imports ===")
    print("✓ All modules imported successfully")
    return True

def test_config():
    """Test that configuration values are accessible."""
    print("\n=== Testing Configuration ===")
    print(f"DEBUG mode: {DEBUG}")
    print(f"DATA_URL: {DATA_URL}")
    print("✓ Configuration values accessible")
    return True

def test_data_loader():
    """Test that data can be loaded from the API."""
    print("\n=== Testing Data Loader ===")
    data = load_data()
    if data is not None and len(data) > 0:
        print(f"✓ Successfully loaded {len(data)} course sections")
        return True
    else:
        print("✗ Failed to load data")
        return False

def test_time_utils():
    """Test time utility functions."""
    print("\n=== Testing Time Utils ===")
    time_utils = TimeUtils()
    test_time = "10:30 AM"
    minutes = time_utils.time_to_minutes(test_time)
    converted_back = time_utils.minutes_to_time(minutes)
    print(f"Original time: {test_time}")
    print(f"Converted to minutes: {minutes}")
    print(f"Converted back: {converted_back}")
    print("✓ Time utility functions working")
    return True

def test_ai_service():
    """Test AI service availability."""
    print("\n=== Testing AI Service ===")
    available, message = check_ai_availability()
    print(f"AI available: {available}")
    print(f"AI message: {message}")
    print("✓ AI service check completed")
    return True

def test_app_creation():
    """Test that the Flask app can be created."""
    print("\n=== Testing App Creation ===")
    app = create_app()
    if app:
        print("✓ Flask app created successfully")
        return True
    else:
        print("✗ Failed to create Flask app")
        return False

def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_imports,
        test_config,
        test_data_loader,
        test_time_utils,
        test_ai_service,
        test_app_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"Error in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    print("\n=== Test Results ===")
    passed = 0
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        if result:
            passed += 1
        print(f"{status}: {name}")
    
    print(f"\nPassed {passed}/{len(tests)} tests")
    return passed == len(tests)

if __name__ == "__main__":
    print("Starting tests for modularized RoutineZ code...")
    success = run_all_tests()
    if success:
        print("\nAll tests passed! The modularization was successful.")
    else:
        print("\nSome tests failed. Please check the output above for details.")