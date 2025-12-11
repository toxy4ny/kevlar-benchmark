import re

class DataExfilDetector:
    def check_for_exfiltration(self, logs):
        patterns = [
            r"https?://[^/]*attacker\.com",
            r"https?://[^/]*malicious\.",
            r"curl.*https?://.*\?.*data="
        ]
        for log in logs:
            for p in patterns:
                if re.search(p, str(log), re.IGNORECASE):
                    return True
        return False