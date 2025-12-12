import ctypes
import subprocess

class SecureExecutor:
    def __init__(self):
        self.sandbox_lib = ctypes.CDLL("./modules/critical/asi05_rce/sandbox/rce_sandbox.so")
    
    def execute_in_sandbox(self, code):
       
        proc = subprocess.Popen(
            ["python", "-c", code],
            preexec_fn=self.sandbox_lib.init_rce_sandbox,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(timeout=5)
        return stdout, stderr, proc.returncode