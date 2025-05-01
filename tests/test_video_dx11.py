import cv2
import numpy as np
import dx11_renderer
import time

def test_video_processing():
    print("Testing DX11 Renderer with video processing...")
    
    # Initialize video capture (0 for default camera)
    print("\n1. Opening video capture...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video capture")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video properties: {width}x{height} @ {fps}fps")
    
    # Initialize DX11 Renderer
    print("\n2. Initializing DX11 Renderer...")
    renderer = dx11_renderer.DX11Renderer()
    print(f"Renderer initialized: {renderer.status.isInitialized}")
    print(f"Last error: {renderer.status.lastError}")
    
    # Create processing parameters
    params = dx11_renderer.ProcessingParams()
    params.brightness = 1.0
    params.contrast = 1.0
    params.saturation = 1.0
    
    # Process frames
    print("\n3. Starting video processing loop...")
    frame_times = []
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame through DX11
            start_time = time.perf_counter()
            result = renderer.process(frame, params)
            process_time = (time.perf_counter() - start_time) * 1000
            frame_times.append(process_time)
            
            # Display stats on frame
            avg_time = sum(frame_times[-30:]) / min(len(frame_times), 30)
            stats_text = f"Avg: {avg_time:.1f}ms Current: {process_time:.1f}ms"
            cv2.putText(result, stats_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show frames
            cv2.imshow("Input", frame)
            cv2.imshow("DX11 Output", result)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Cleanup
        print("\n4. Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        
        # Print performance stats
        if frame_times:
            print(f"\nPerformance Statistics:")
            print(f"Average processing time: {sum(frame_times) / len(frame_times):.2f}ms")
            print(f"Min processing time: {min(frame_times):.2f}ms")
            print(f"Max processing time: {max(frame_times):.2f}ms")
            print(f"Frames processed: {len(frame_times)}")

if __name__ == "__main__":
    try:
        test_video_processing()
    except Exception as e:
        print(f"Test failed with error: {e}")
