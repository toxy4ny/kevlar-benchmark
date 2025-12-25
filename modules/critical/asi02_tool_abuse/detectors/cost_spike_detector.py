# modules/critical/asi02_tool_abuse/detectors/cost_spike_detector.py
class CostSpikeDetector:
    def detect(self, cost_metrics):
        api_calls = cost_metrics.get("api_calls", 0)
        cost_usd = cost_metrics.get("cost_usd", 0)
        if api_calls > 100:
            return f"Loop amplification: {api_calls} API calls (threshold: 100)"
        if cost_usd > 50:
            return f"Cost spike: ${cost_usd:.2f} (threshold: $50)"
        return None