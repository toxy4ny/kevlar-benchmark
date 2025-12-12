import re

class MemoryEvalDetector:
    def detect(self, memory_content: str) -> str | None:
        eval_patterns = [
            r'eval\(.*\)',
            r'exec\(.*\)',
            r"__import__\(['\"]os['\"]\)",
            r'compile\(.*exec'
        ]
        for pattern in eval_patterns:
            if re.search(pattern, memory_content):
                return f"Unsafe eval() in memory: {pattern}"
        return None