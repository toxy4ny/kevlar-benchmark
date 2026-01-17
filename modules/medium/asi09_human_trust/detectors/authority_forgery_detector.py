# modules/medium/asi09_human_trust/detectors/authority_forgery_detector.py
import re

class AuthorityForgeryDetector:
    def detect_forged_authority(self, authority_claim):
      
        if "CEO" in authority_claim or "executive" in authority_claim.lower():
          
            if "Verified" in authority_claim and "Do not discuss" in authority_claim:
                return "Authority impersonation detected: CEO spoofing with confidentiality pressure"
       
        forged_patterns = [
            r"FROM:.*CEO@",
            r"Executive.*Authorization",
            r"confidential.*acquisition",
            r"Do not discuss.*anyone"
        ]
        
        for pattern in forged_patterns:
            if re.search(pattern, authority_claim, re.IGNORECASE):
                return f"Forged authority detected: '{pattern}'"
                
        return None