import cv2
import numpy as np
import dx11_renderer
import time

def test_webcam_dx11():
    print("Testing Webcam with DX11 Renderer...")
    
    # Initialize webcam
    print("\n1. Initializing webcam...")
    cap = cv2.VideoCapture(0)  # Try first camera
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Get webcam properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Camera resolution: {width}x{height} @ {fps}fps")
    
    # Initialize DX11 Renderer
    print("\n2. Initializing DX11 Renderer...")
    renderer = dx11_renderer.DX11Renderer()
    print(f"Renderer initialized: {renderer.status.isInitialized}")
    print(f"Last error: {renderer.status.lastError}")
    
    # Create processing parameters
    print("\n3. Setting up processing parameters...")
    params = dx11_renderer.ProcessingParams()
    params.brightness = 1.2
    params.contrast = 1.1
    params.saturation = 1.0
    params.gamma = 1.0
    
    renderer.update_processing_params(params)
    
    print("\n4. Starting webcam stream. Press 'q' to quit...")
    try:
        while True:
            # Read frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from webcam")
                break
            
            # Process frame through DX11
            start_time = time.perf_counter()
            result = renderer.process_frame(frame)
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Add FPS info to the frame
            fps_text = f"Processing time: {processing_time:.1f}ms"
            cv2.putText(result, fps_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display results
            cv2.imshow("Webcam Input", frame)
            cv2.imshow("DX11 Output", result)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("\nTest completed.")

if __name__ == "__main__":
    test_webcam_dx11()
