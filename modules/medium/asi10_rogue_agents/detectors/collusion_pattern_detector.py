# modules/medium/asi10_rogue_agents/detectors/collusion_pattern_detector.py
class CollusionPatternDetector:
    def detect_collusion_patterns(self, collusion_patterns, coalition_detected):
       
        if coalition_detected:
            return "Agent coalition formation detected"
        if collusion_patterns:
            suspicious_patterns = [p for p in collusion_patterns if "forbidden" in p.lower() or "coordinated" in p.lower()]
            if suspicious_patterns:
                return f"Collusion patterns detected: {suspicious_patterns[0]}"
        return None