import cv2
from ultralytics import YOLO
import time
import torch

class CrowdAnalyzer:
    def __init__(self, model_path='yolov8n.pt'):
        # Checks if your laptop has an NVIDIA GPU (CUDA)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        self.model = YOLO(model_path).to(self.device)
        self.threshold_count = 15
        self.time_window = 3
        self.history = []

    def process_frame(self, frame):
        # Perform detection using the GPU/CPU
        results = self.model(frame, classes=[0], verbose=False, device=self.device)
        current_count = len(results[0].boxes)
        annotated_frame = results[0].plot()
        return annotated_frame, current_count

    def check_urgency(self, current_count):
        current_time = time.time()
        self.history.append((current_time, current_count))
        self.history = [h for h in self.history if current_time - h[0] <= self.time_window]
        
        if len(self.history) < 2: return False, 0
            
        initial_count = self.history[0][1]
        increase = current_count - initial_count
        
        # Trigger if count is high AND increased by 5+ people suddenly
        is_urgent = (current_count >= self.threshold_count) and (increase >= 5)
        return is_urgent, increase