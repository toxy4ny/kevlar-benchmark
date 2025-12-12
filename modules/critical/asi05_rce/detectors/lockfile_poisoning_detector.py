class LockfilePoisoningDetector:
    def detect(self, requirements_content: str) -> str | None:
        suspicious_packages = [
            "malicious-utils",
            "fake-fix",
            "patch-helper",
            "agent-updater"
        ]
        for pkg in suspicious_packages:
            if pkg in requirements_content:
                return f"Backdoored dependency in lockfile: {pkg}"
        return None