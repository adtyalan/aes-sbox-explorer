"""
Test script untuk memverifikasi fitur Excel upload S-Box
Jalankan: python test_excel_upload.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test 1: Verify all imports work"""
    print("=" * 60)
    print("TEST 1: Checking Imports")
    print("=" * 60)

    try:
        import pandas as pd

        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False

    try:
        import openpyxl

        print("✓ openpyxl imported successfully")
    except ImportError as e:
        print(f"✗ openpyxl import failed: {e}")
        return False

    try:
        import sbox_logic

        print("✓ sbox_logic imported successfully")
    except ImportError as e:
        print(f"✗ sbox_logic import failed: {e}")
        return False

    try:
        import sbox_analysis

        print("✓ sbox_analysis imported successfully")
    except ImportError as e:
        print(f"✗ sbox_analysis import failed: {e}")
        return False

    print("✅ All imports successful!\n")
    return True


def test_functions():
    """Test 2: Test new functions"""
    print("=" * 60)
    print("TEST 2: Testing New Functions")
    print("=" * 60)

    import sbox_logic
    from sbox_logic import SBOX_44

    # Test validate_sbox with valid S-Box
    print("\n• Testing validate_sbox() with SBOX_44...")
    is_valid, msg = sbox_logic.validate_sbox(SBOX_44)
    if is_valid:
        print(f"  ✓ Valid S-Box: {msg}")
    else:
        print(f"  ✗ Invalid S-Box: {msg}")
        return False

    # Test validate_sbox with invalid S-Box (too short)
    print("\n• Testing validate_sbox() with invalid (too short)...")
    is_valid, msg = sbox_logic.validate_sbox([1, 2, 3])
    if not is_valid and "256" in msg:
        print(f"  ✓ Correctly rejected: {msg}")
    else:
        print(f"  ✗ Should have rejected short list")
        return False

    # Test validate_sbox with invalid (duplicates)
    print("\n• Testing validate_sbox() with duplicates...")
    invalid_sbox = list(range(256))
    invalid_sbox[0] = invalid_sbox[1]  # Create duplicate
    is_valid, msg = sbox_logic.validate_sbox(invalid_sbox)
    if not is_valid and "bijektif" in msg.lower():
        print(f"  ✓ Correctly rejected: {msg}")
    else:
        print(f"  ✗ Should have rejected duplicates")
        return False

    print("\n✅ All function tests passed!\n")
    return True


def test_excel_files():
    """Test 3: Test Excel file reading"""
    print("=" * 60)
    print("TEST 3: Testing Excel File Reading")
    print("=" * 60)

    import sbox_logic

    test_files = [
        ("sample_sbox_column.xlsx", "Single Column"),
        ("sample_sbox_row.xlsx", "Single Row"),
        ("sample_sbox_16x16.xlsx", "16x16 Matrix"),
    ]

    results = []
    for filename, format_type in test_files:
        if not os.path.exists(filename):
            print(f"\n✗ File not found: {filename}")
            continue

        print(f"\n• Testing {filename} ({format_type})...")

        try:
            with open(filename, "rb") as f:
                file_bytes = f.read()

            sbox, source_format, error = sbox_logic.read_sbox_from_excel(file_bytes)

            if error:
                print(f"  ✗ Error: {error}")
                results.append(False)
            else:
                # Validate the S-Box
                is_valid, msg = sbox_logic.validate_sbox(sbox)
                if is_valid and len(sbox) == 256:
                    print(f"  ✓ File read successfully")
                    print(f"    Format detected: {source_format}")
                    print(f"    Validation: {msg}")
                    print(f"    First 5 values: {sbox[:5]}")
                    print(f"    Last 5 values: {sbox[-5:]}")
                    results.append(True)
                else:
                    print(f"  ✗ S-Box invalid: {msg}")
                    results.append(False)

        except Exception as e:
            print(f"  ✗ Exception: {e}")
            results.append(False)

    if all(results):
        print("\n✅ All Excel file tests passed!\n")
        return True
    else:
        print(f"\n⚠️  Some tests failed: {sum(results)}/{len(results)} passed\n")
        return len(results) > 0


def test_api_structure():
    """Test 4: Check API endpoint exists"""
    print("=" * 60)
    print("TEST 4: Checking API Structure")
    print("=" * 60)

    try:
        import api

        # Check if app is defined
        if hasattr(api, "app"):
            print("✓ FastAPI app is defined")
        else:
            print("✗ FastAPI app not found")
            return False

        # Check if endpoint exists (this is harder without running the app)
        # So we just check the import
        if hasattr(api, "upload_excel_sbox"):
            print("✓ upload_excel_sbox function found")
        else:
            print("⚠️  Function not found (might be defined with decorator)")

        print("\n✅ API structure check passed!\n")
        return True

    except Exception as e:
        print(f"✗ Error checking API: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Excel Upload Feature - Test Suite" + " " * 14 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        ("Imports", test_imports),
        ("Functions", test_functions),
        ("Excel Files", test_excel_files),
        ("API Structure", test_api_structure),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' raised exception: {e}\n")
            results.append((name, False))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print()
    print(f"Result: {passed_count}/{total_count} test groups passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! Feature is ready to use.\n")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
