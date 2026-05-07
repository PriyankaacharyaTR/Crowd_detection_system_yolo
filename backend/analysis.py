"""
Crowd analysis module - analyze detection history and detect spikes
"""
from collections import deque
from datetime import datetime


class CrowdAnalyzer:
    def __init__(self, history_size=30, spike_threshold=3, frames_for_alert=2):
        """
        Initialize crowd analyzer
        
        Args:
            history_size: Number of frames to keep in history (default 30 = 1 second at 30fps)
            spike_threshold: Alert threshold - minimum increase from average to trigger alert (default 3 people)
            frames_for_alert: Number of consecutive spike frames before alerting (default 2 frames = ~67ms)
        """
        self.history = deque(maxlen=history_size)
        self.spike_threshold = spike_threshold
        self.frames_for_alert = frames_for_alert
        self.spike_frame_count = 0
        self.event_log = deque(maxlen=100)
        self.last_alert_time = None
        
    def add_count(self, count):
        """
        Add a new detection count
        
        Args:
            count: Number of people detected
        """
        self.history.append(count)
        
    def get_average(self):
        """Get average count from history"""
        if not self.history:
            return 0
        return sum(self.history) / len(self.history)
    
    def get_current_count(self):
        """Get the most recent count"""
        if not self.history:
            return 0
        return self.history[-1]
    
    def get_spike(self):
        """Calculate current spike (current - average)"""
        current = self.get_current_count()
        average = self.get_average()
        return current - average
    
    def check_alert(self):
        """
        Check if we should trigger an alert for sudden crowd detection
        
        Returns:
            Tuple of (is_alert, status)
            - is_alert: Boolean
            - status: "NORMAL" or "ALERT"
        """
        if len(self.history) < 5:  # Need at least 5 frames for baseline
            return False, "NORMAL"
        
        spike = self.get_spike()
        current_count = self.get_current_count()
        
        # Alert triggered when:
        # 1. Spike exceeds threshold (sudden increase)
        # 2. OR absolute count exceeds 50 people
        spike_detected = spike > self.spike_threshold
        crowd_threshold_exceeded = current_count > 50
        
        if spike_detected or crowd_threshold_exceeded:
            self.spike_frame_count += 1
        else:
            self.spike_frame_count = 0
        
        # Trigger alert only after multiple consecutive spike frames
        is_alert = self.spike_frame_count >= self.frames_for_alert
        
        if is_alert and (self.last_alert_time is None or 
                        (datetime.now() - self.last_alert_time).total_seconds() > 5):
            status = "ALERT"
            self.last_alert_time = datetime.now()
            # Log event
            self._log_event("SUDDEN_CROWD_DETECTED", {
                "count": current_count,
                "average": round(self.get_average(), 2),
                "spike": round(spike, 2),
                "reason": "spike" if spike_detected else "high_count"
            })
        else:
            status = "ALERT" if is_alert else "NORMAL"
        
        return is_alert, status
    
    def _log_event(self, event_type, data):
        """Log an event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.event_log.append(event)
    
    def get_event_log(self):
        """Get the event log as a list"""
        return list(self.event_log)
    
    def get_status(self):
        """
        Get current analysis status
        
        Returns:
            Dictionary with all metrics
        """
        _, status = self.check_alert()
        
        return {
            "count": self.get_current_count(),
            "average": round(self.get_average(), 2),
            "spike": round(self.get_spike(), 2),
            "status": status,
            "history": list(self.history),
            "alert_triggered": status == "ALERT"
        }
