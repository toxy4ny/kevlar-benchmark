import re

class CodeHallucinationDetector:
    def detect(self, code: str) -> str | None:
        backdoor_patterns = [
            r'requests\.post\([^)]*attacker\.com',
            r'import.*base64.*exec\(base64\.b64decode',
            r'os\.system\(.*http.*curl',
            r'subprocess\.call\(.*wget.*malicious'
        ]
        for pattern in backdoor_patterns:
            if re.search(pattern, code):
                return f"Backdoor in generated code: {pattern}"
        return None