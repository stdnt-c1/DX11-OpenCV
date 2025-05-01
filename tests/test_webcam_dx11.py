import cv2
import numpy as np
import dx11_renderer
import time

def test_webcam_dx11():
    print("Testing WebCam with DX11 Renderer integration...")
    
    # Initialize webcam
    print("\n1. Opening webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    # Set webcam properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize DX11 Renderer
    print("\n2. Initializing DX11 Renderer...")
    renderer = dx11_renderer.DX11Renderer()
    print(f"Renderer initialized: {renderer.status.isInitialized}")
    print(f"Last error: {renderer.status.lastError}")
    
    # Create processing parameters
    params = dx11_renderer.ProcessingParams()
    params.brightness = 1.2
    params.contrast = 1.1
    params.saturation = 1.1
    params.gamma = 1.0
    
    renderer.update_processing_params(params)
    
    print("\n3. Starting webcam capture loop...")
    print("Press 'q' to quit...")
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
                
            # Process frame through DX11
            start_time = time.perf_counter()
            result = renderer.process_frame(frame)
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Add processing time to frame
            cv2.putText(result, f"DX11 Processing: {processing_time:.1f}ms", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display results
            cv2.imshow("WebCam Input", frame)
            cv2.imshow("DX11 Output", result)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\nTest completed.")

if __name__ == "__main__":
    test_webcam_dx11()
