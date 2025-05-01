import os
import sys
import cv2
import numpy as np
import time
import json
import torch
from ultralytics import YOLO

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
print("PyTorch version:", torch.__version__)
print("Looking for dx11_renderer in:", release_dir)

try:
    print("\nImporting dx11_renderer module...")
    import dx11_renderer
    print("Successfully imported dx11_renderer module")
except ImportError as e:
    print(f"Failed to import dx11_renderer module: {e}")
    sys.exit(1)

class YOLOProcessor:
    def __init__(self, model_name='yolov8n.pt'):
        print(f"\nLoading YOLO model: {model_name}")
        self.model = YOLO(model_name)
        self.classes = self.model.names
        print(f"Model loaded successfully with {len(self.classes)} classes")

    def process_frame(self, frame):
        results = self.model(frame, stream=True)
        return next(results)

    def draw_detections(self, frame, result, confidence_threshold=0.3):
        for r in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            if score > confidence_threshold:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                label = f"{self.classes[int(class_id)]}: {score:.2f}"
                cv2.putText(frame, label, (int(x1), int(y1 - 10)),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
    print("\nInitializing renderer and YOLO...")
    try:
        renderer = dx11_renderer.DX11Renderer()
        params = dx11_renderer.ProcessingParams()
        yolo = YOLOProcessor()
        print("Successfully initialized DX11Renderer and YOLO")
    except Exception as e:
        print(f"Error during initialization: {e}")
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

        print("\nSetting up display windows...")
        cv2.namedWindow('Original vs Processed', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)

        # Create trackbars for parameter control
        cv2.createTrackbar('Brightness', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Contrast', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Saturation', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Gamma', 'Controls', 100, 1000, lambda x: None)
        cv2.createTrackbar('Detection Confidence', 'Controls', 30, 100, lambda x: None)

        # Print control instructions
        print("\nControls:")
        print("- Adjust sliders to change parameters")
        print("- Press 'r' to reset parameters")
        print("- Press 's' to save current preset")
        print("- Press 'l' to load last preset")
        print("- Press 'p' to save screenshot")
        print("- Press 'd' to toggle detection overlay")
        print("- Press 'q' to quit")

        print("\nStarting main processing loop...")
        frame_count = 0
        fps = 0
        last_time = time.time()
        show_detections = True
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error reading frame")
                break

            # Update parameters from trackbars
            params.brightness = cv2.getTrackbarPos('Brightness', 'Controls') / 100.0
            params.contrast = cv2.getTrackbarPos('Contrast', 'Controls') / 100.0
            params.saturation = cv2.getTrackbarPos('Saturation', 'Controls') / 100.0
            params.gamma = cv2.getTrackbarPos('Gamma', 'Controls') / 100.0
            confidence_threshold = cv2.getTrackbarPos('Detection Confidence', 'Controls') / 100.0
            
            # Validate parameters
            params = validate_params(params)

            # Process frame with DX11
            renderer.update_processing_params(params)
            processed_frame = renderer.process_frame(frame)

            # Run YOLO detection on processed frame
            if show_detections:
                result = yolo.process_frame(processed_frame)
                yolo.draw_detections(processed_frame, result, confidence_threshold)

            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - last_time)
                last_time = current_time

            # Display frames with performance metrics
            status = renderer.get_status()
            combined_frame = np.hstack((frame, processed_frame))
            cv2.putText(combined_frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(combined_frame, f"GPU Time: {status.lastProcessingTime:.1f}ms", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Original vs Processed", combined_frame)

            # Create info display with performance metrics
            status = renderer.get_status()
            info_display = np.zeros((250, 400), dtype=np.uint8)
            texts = [
                "Performance:",
                f"GPU Time: {status.lastProcessingTime:.1f}ms",
                f"FPS: {fps:.1f}",
                f"Resolution: {status.textureWidth}x{status.textureHeight}",
                "",
                "Parameters:",
                f"Brightness: {params.brightness:.2f}",
                f"Contrast: {params.contrast:.2f}",
                f"Saturation: {params.saturation:.2f}",
                f"Gamma: {params.gamma:.2f}",
                f"Confidence: {confidence_threshold:.2f}",
                f"Detection: {'On' if show_detections else 'Off'}",
                "Press 'r' to reset",
                "Press 's' to save preset",
                "Press 'd' to toggle detection"
            ]
            for i, text in enumerate(texts):
                cv2.putText(info_display, text, (10, 20 + i*20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("Controls", info_display)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nUser requested exit")
                break
            elif key == ord('r'):
                params = dx11_renderer.ProcessingParams()
                update_trackbars('Controls', params)
                print("\nReset parameters to defaults")
            elif key == ord('s'):
                save_preset(params)
            elif key == ord('l'):
                loaded_params = load_preset()
                if loaded_params:
                    params = loaded_params
                    update_trackbars('Controls', params)
            elif key == ord('p'):
                os.makedirs("screenshots", exist_ok=True)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"screenshots/processed_{timestamp}.png"
                cv2.imwrite(filename, combined_frame)
                print(f"\nSaved screenshot to {filename}")
            elif key == ord('d'):
                show_detections = not show_detections
                print(f"\nDetection overlay: {'On' if show_detections else 'Off'}")

    except Exception as e:
        print(f"Error in main loop: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        print("\nCleaning up...")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
