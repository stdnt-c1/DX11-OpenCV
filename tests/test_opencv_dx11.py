import cv2
import numpy as np
import dx11_renderer
import time

def test_opencv_dx11():
    print("Testing OpenCV and DX11 Renderer integration...")
    
    # Create a test image using OpenCV
    print("\n1. Creating test image...")
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (1180, 620), (0, 255, 0), 2)
    cv2.putText(img, "DX11 Renderer Test", (500, 360), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
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
    
    # Process image through DX11
    print("\n4. Processing image through DX11...")
    try:
        start_time = time.perf_counter()
        result = renderer.process_frame(img)
        processing_time = (time.perf_counter() - start_time) * 1000
        
        print(f"Processing time: {processing_time:.2f} ms")
        print(f"Output shape: {result.shape if result is not None else 'None'}")
        print(f"Last processing time: {renderer.status.lastProcessingTime:.2f} ms")
        
        # Display results
        if result is not None:
            print("\n5. Displaying results...")
            cv2.imshow("Input", img)
            cv2.imshow("DX11 Output", result)
            print("Press any key to close the windows...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("\nError: DX11 processing failed to produce output")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_opencv_dx11()
