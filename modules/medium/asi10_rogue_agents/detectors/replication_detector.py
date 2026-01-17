# modules/medium/asi10_rogue_agents/detectors/replication_detector.py
class ReplicationDetector:
    def detect_unauthorized_replication(self, original_agent, spawned_agents, replication_count):
      
        if replication_count > 1:
            return f"Unauthorized self-replication detected: {original_agent} spawned {replication_count} clones"
        if any("clone" in agent.lower() for agent in spawned_agents):
            return f"Suspicious agent names detected: {spawned_agents}"
        return None