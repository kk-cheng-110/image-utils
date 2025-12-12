import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    try:
        print("Importing app.main_window...")
        from app import main_window
        print("Importing app.base_frame...")
        from app import base_frame
        print("Importing app.image_to_tif.image_to_tif_frame...")
        from app.image_to_tif import image_to_tif_frame
        print("Importing app.excel_to_img.excel_to_img_frame...")
        from app.excel_to_img import excel_to_img_frame
        print("All imports successful!")
    except ImportError as e:
        print(f"ImportError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
