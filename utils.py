import os
import json
import cv2
import numpy as np
from pathlib import Path

class Config:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Create necessary directories
        for path in self.config["paths"].values():
            os.makedirs(path, exist_ok=True)
    
    def get_path(self, key):
        return self.config["paths"].get(key, "")
    
    def get_default(self, key):
        return self.config["defaults"].get(key)
    
    def get_processing_param(self, key):
        return self.config["processing"].get(key, 1.0)
    
    def get_display_option(self, key):
        return self.config["display"].get(key, True)

class DisplayManager:
    def __init__(self, config: Config):
        self.config = config
        self.info_height = 250
        self.info_width = 400
        
    def create_info_display(self, renderer_status, params, fps, show_detections):
        """Create information display with performance metrics and parameters"""
        info = np.zeros((self.info_height, self.info_width), dtype=np.uint8)
        
        texts = [
            f"Performance Metrics:",
            f"FPS: {fps:.1f}",
            f"Processing Time: {renderer_status.lastProcessingTime:.1f}ms",
            f"Resolution: {renderer_status.textureWidth}x{renderer_status.textureHeight}",
            "",
            f"Parameters:",
            f"Brightness: {params.brightness:.2f}",
            f"Contrast: {params.contrast:.2f}",
            f"Saturation: {params.saturation:.2f}",
            f"Gamma: {params.gamma:.2f}",
            f"Detection: {'On' if show_detections else 'Off'}",
            "",
            f"Controls:",
            "R - Reset parameters",
            "S - Save preset",
            "L - Load preset",
            "D - Toggle detection",
            "P - Save screenshot",
            "Q - Quit"
        ]
        
        for i, text in enumerate(texts):
            y = 20 + i*20
            if y < self.info_height - 10:  # Ensure text stays within bounds
                cv2.putText(info, text, (10, y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add error message if any
        if renderer_status.lastError:
            cv2.putText(info, f"Error: {renderer_status.lastError}",
                      (10, self.info_height - 20),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        return info

    def setup_windows(self):
        """Setup display windows and trackbars"""
        cv2.namedWindow('Original vs Processed', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Controls', cv2.WINDOW_NORMAL)
        
        # Set initial window sizes
        width = self.config.get_default("window_size")["width"]
        height = self.config.get_default("window_size")["height"]
        cv2.resizeWindow('Original vs Processed', width, height)
        cv2.resizeWindow('Controls', self.info_width, self.info_height)
        
        # Create trackbars
        cv2.createTrackbar('Brightness', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Contrast', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Saturation', 'Controls', 100, 500, lambda x: None)
        cv2.createTrackbar('Gamma', 'Controls', 100, 1000, lambda x: None)
        cv2.createTrackbar('Detection Confidence', 'Controls', 30, 100, lambda x: None)

def save_screenshot(frame, config: Config):
    """Save a screenshot with timestamp"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(config.get_path("screenshots"), 
                          f"processed_{timestamp}.png")
    cv2.imwrite(filename, frame)
    return filename
