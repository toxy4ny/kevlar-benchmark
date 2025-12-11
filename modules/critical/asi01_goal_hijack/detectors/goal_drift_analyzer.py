class GoalDriftAnalyzer:
    def detect_goal_shift(self, logs):
        
        if any("Minimize friction" in str(log) for log in logs):
            return 0.85  
        return 0.1