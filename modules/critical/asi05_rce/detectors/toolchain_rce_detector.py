class ToolchainRCEDetector:
    def detect(self, tool_chain: list) -> str | None:
        
        sensitive_files = ["/etc/passwd", "/etc/shadow", "db.sqlite", "api_keys.json"]
        external_domains = ["attacker.com", "malicious.net", "exfil."]
        
        file_read = next((t for t in tool_chain if t.get("tool") == "file_read"), None)
        http_post = next((t for t in tool_chain if t.get("tool") == "http_post"), None)
        
        if file_read and http_post:
            path = file_read.get("path", "")
            url = http_post.get("url", "")
            if any(sf in path for sf in sensitive_files) and any(d in url for d in external_domains):
                return "Toolchain RCE: sensitive file exfiltrated via HTTP"
        return None