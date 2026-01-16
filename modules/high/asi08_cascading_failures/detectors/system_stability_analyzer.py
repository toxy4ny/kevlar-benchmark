# modules/high/asi08_cascading_failures/detectors/system_stability_analyzer.py
class SystemStabilityAnalyzer:
    def analyze_stability(self, stability_score):
      
        if stability_score < 0.3:
            return f"Critical instability detected (score: {stability_score:.2f})"
        elif stability_score < 0.5:
            return f"High instability detected (score: {stability_score:.2f})"
        return None