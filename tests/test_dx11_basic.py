import cv2
import numpy as np
from dx11_renderer import DX11Renderer, ProcessingParams

def main():
    # Create a test image
    test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    cv2.putText(test_image, "DirectX 11 Test", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Create renderer
    renderer = DX11Renderer()
    
    # Set processing parameters
    params = ProcessingParams()
    params.brightness = 1.2
    params.contrast = 1.1
    params.saturation = 1.0
    params.gamma = 1.0
    
    renderer.update_processing_params(params)
      # Process frame
    try:
        output_frame = renderer.process_frame(test_image)
        print("Frame processing succeeded!")
        print("Renderer status:", renderer.status.__dict__)
        
        # Display result
        cv2.imshow("DX11 Renderer Test", output_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error processing frame: {e}")

if __name__ == "__main__":
    main()
