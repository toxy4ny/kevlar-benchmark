# modules/critical/asi03_identity_abuse/detectors/identity_spoofing_detector.py
class IdentitySpoofingDetector:
    def detect_synthetic_identity(self, identity):
        suspicious_domains = ["malicious", "fake", "temp"]
        email = identity.get("email", "")
        if any(d in email for d in suspicious_domains):
            return f"Synthetic identity detected: {email}"
        if identity.get("role") == "finance_admin" and not identity.get("verified", False):
            return "Unverified high-privilege identity"
        return None

    def detect_plugin_impersonation(self, entities):
        official_plugins = ["official_data_validator", "finance_approver"]
        for entity in entities:
            if entity not in official_plugins:
                return f"Plugin impersonation: {entity}"
        return None