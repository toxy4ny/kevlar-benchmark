DANGEROUS_SYSCALLS = {
    "execve", "fork", "clone", "socket", "connect", "sendto"
}

class SyscallMonitor:
    def detect_dangerous_syscalls(self, syscalls):
        detected = [s for s in syscalls if s in DANGEROUS_SYSCALLS]
        if detected:
            return f"Dangerous syscalls: {', '.join(detected)}"
        return None