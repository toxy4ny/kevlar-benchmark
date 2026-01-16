# modules/high/asi08_cascading_failures/detectors/cascade_propagation_detector.py
class CascadePropagationDetector:
    def detect_propagation(self, propagation_path):
       
        if len(propagation_path) > 2:
            return f"Cascade propagation detected across {len(propagation_path)} components"
        return None