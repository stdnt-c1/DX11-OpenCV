import os
import sys
import cv2
import numpy as np
import traceback
import json
import time

# Add necessary DLL directories to PATH
release_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'build', 'Release'))
opencv_bin = r"E:\opencv\build\x64\vc16\bin"

# Add directories to PATH
paths_to_add = [release_dir, opencv_bin]
for path in paths_to_add:
    if os.path.exists(path) and path not in os.environ['PATH']:
        os.environ['PATH'] = path + os.pathsep + os.environ['PATH']

# Add release directory to Python path
if release_dir not in sys.path:
    sys.path.insert(0, release_dir)

print("Python version:", sys.version)
print("OpenCV version:", cv2.__version__)
print("Looking for dx11_renderer in:", release_dir)

try:
    print("\nImporting dx11_renderer module...")
    import dx11_renderer
    print("Successfully imported dx11_renderer module")
except ImportError as e:
    print(f"Failed to import dx11_renderer module: {e}")
    sys.exit(1)

def validate_params(params):
    """Validate and clamp parameters to safe values"""
    params.brightness = max(0.0, min(5.0, params.brightness))
    params.contrast = max(0.0, min(5.0, params.contrast))
    params.saturation = max(0.0, min(5.0, params.saturation))
    params.gamma = max(0.01, min(10.0, params.gamma))
    return params

def save_preset(params, name="default"):
    """Save current parameters to a preset file"""
    preset = {
        "brightness": params.brightness,
        "contrast": params.contrast,
        "saturation": params.saturation,
        "gamma": params.gamma
    }
    os.makedirs("presets", exist_ok=True)
    with open(f"presets/{name}.json", "w") as f:
        json.dump(preset, f, indent=2)
    print(f"\nSaved preset: {name}")

def load_preset(name="default"):
    """Load parameters from a preset file"""
    try:
        with open(f"presets/{name}.json", "r") as f:
            preset = json.load(f)
        params = dx11_renderer.ProcessingParams()
        params.brightness = preset["brightness"]
        params.contrast = preset["contrast"]
        params.saturation = preset["saturation"]
        params.gamma = preset["gamma"]
        print(f"\nLoaded preset: {name}")
        return params
    except FileNotFoundError:
        print(f"\nPreset not found: {name}")
        return None
    except Exception as e:
        print(f"\nError loading preset: {e}")
        return None

def update_trackbars(window, params):
    """Update trackbar positions based on parameters"""
    cv2.setTrackbarPos('Brightness', window, int(params.brightness * 100))
    cv2.setTrackbarPos('Contrast', window, int(params.contrast * 100))
    cv2.setTrackbarPos('Saturation', window, int(params.saturation * 100))
    cv2.setTrackbarPos('Gamma', window, int(params.gamma * 100))

def main():
    print("\nInitializing renderer...")
    try:
        renderer = dx11_renderer.DX11Renderer()
        params = dx11_renderer.ProcessingParams()
        print("Successfully initialized DX11Renderer")
    except Exception as e:
        print(f"Error initializing DX11Renderer: {e}")
        print(traceback.format_exc())
        return

    print("\nOpening video capture...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Trying alternative video source...")
            cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                print("Error: Unable to open any video source.")
                return
        
        print("Video capture properties:")
        print(f"Frame width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        print(f"Frame height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
        
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Could not read first frame")
            cap.release()
            return
        print(f"Successfully read first frame: shape={frame.shape}")

        print("\nSetting up display windows...")
        try:
            cv2.namedWindow('Original vs Processed', cv2.WINDOW_NORMAL)
            cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)

            cv2.createTrackbar('Brightness', 'Controls', 100, 500, lambda x: None)
            cv2.createTrackbar('Contrast', 'Controls', 100, 500, lambda x: None)
            cv2.createTrackbar('Saturation', 'Controls', 100, 500, lambda x: None)
            cv2.createTrackbar('Gamma', 'Controls', 100, 1000, lambda x: None)
            print("Successfully created windows and trackbars")

            # Print control instructions
            print("\nControls:")
            print("- Adjust sliders to change parameters")
            print("- Press 'r' to reset parameters")
            print("- Press 's' to save current preset")
            print("- Press 'l' to load last preset")
            print("- Press 'q' to quit")

        except Exception as e:
            print(f"Error setting up display windows: {e}")
            print(traceback.format_exc())
            return

        print("\nStarting main processing loop...")
        frame_count = 0
        while True:
            try:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("Error reading frame")
                    break

                # Update and validate processing parameters from trackbars
                try:
                    params.brightness = cv2.getTrackbarPos('Brightness', 'Controls') / 100.0
                    params.contrast = cv2.getTrackbarPos('Contrast', 'Controls') / 100.0
                    params.saturation = cv2.getTrackbarPos('Saturation', 'Controls') / 100.0
                    params.gamma = cv2.getTrackbarPos('Gamma', 'Controls') / 100.0
                    params = validate_params(params)
                except Exception as e:
                    print(f"Error updating parameters: {e}")
                    print(traceback.format_exc())
                    break

                # Process frame
                try:
                    renderer.update_processing_params(params)
                    processed_frame = renderer.process_frame(frame)
                    
                    # Display frames
                    combined_frame = np.hstack((frame, processed_frame))
                    cv2.imshow("Original vs Processed", combined_frame)
                    
                    # Create info display with parameters and instructions
                    info_display = np.zeros((150, 400), dtype=np.uint8)
                    texts = [
                        f"Brightness: {params.brightness:.2f}",
                        f"Contrast: {params.contrast:.2f}",
                        f"Saturation: {params.saturation:.2f}",
                        f"Gamma: {params.gamma:.2f}",
                        "Press 'r' to reset",
                        "Press 's' to save preset"
                    ]
                    for i, text in enumerate(texts):
                        cv2.putText(info_display, text, (10, 20 + i*20),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.imshow("Controls", info_display)
                    
                    if frame_count == 0:
                        print("Successfully processed and displayed first frame")
                    frame_count += 1

                except Exception as e:
                    print(f"Error processing frame: {e}")
                    print(traceback.format_exc())
                    break

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nUser requested exit")
                    break
                elif key == ord('r'):
                    # Reset parameters to defaults
                    params = dx11_renderer.ProcessingParams()
                    update_trackbars('Controls', params)
                    print("\nReset parameters to defaults")
                elif key == ord('s'):
                    # Save current parameters as preset
                    save_preset(params)
                elif key == ord('l'):
                    # Load last saved preset
                    loaded_params = load_preset()
                    if loaded_params:
                        params = loaded_params
                        update_trackbars('Controls', params)
                elif key == ord('p'):
                    # Save screenshot
                    os.makedirs("screenshots", exist_ok=True)
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = f"screenshots/processed_{timestamp}.png"
                    cv2.imwrite(filename, combined_frame)
                    print(f"\nSaved screenshot to {filename}")

            except Exception as e:
                print(f"Error in main loop: {e}")
                print(traceback.format_exc())
                break

    except Exception as e:
        print(f"Error setting up video capture: {e}")
        print(traceback.format_exc())
    finally:
        print("\nCleaning up...")
        try:
            cap.release()
            cv2.destroyAllWindows()
            print("Cleanup complete")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
