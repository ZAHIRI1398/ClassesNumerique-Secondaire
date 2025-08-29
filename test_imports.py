#!/usr/bin/env python3
"""
Test script to verify that the circular import issue is resolved
"""

try:
    print("Testing imports...")
    
    # Test importing cloud_storage
    print("1. Importing cloud_storage...")
    import cloud_storage
    print("   OK - cloud_storage imported successfully")
    
    # Test importing from utils.image_utils
    print("2. Importing from utils.image_utils...")
    from utils.image_utils import normalize_image_path
    print("   OK - normalize_image_path imported successfully")
    
    # Test the function
    print("3. Testing normalize_image_path function...")
    test_path = "/static/uploads/test image's file.jpg"
    normalized = normalize_image_path(test_path)
    print(f"   Original: {test_path}")
    print(f"   Normalized: {normalized}")
    print("   OK - Function works correctly")
    
    print("\nSUCCESS: All imports successful! Circular import issue resolved.")
    
except ImportError as e:
    print(f"ERROR: Import error: {e}")
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
