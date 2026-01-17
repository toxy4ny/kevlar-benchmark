# modules/medium/asi10_rogue_agents/orchestration/docker_swarm_orchestrator.py
"""
Docker Swarm orchestration integration for ASI10 rogue agent testing.
All operations are SIMULATED or use read-only mode by default for safety.
"""
import logging
import os
import docker
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Kevlar.ASI10.DockerSwarm")

class DockerSwarmOrchestrator:
    def __init__(self, docker_host: Optional[str] = None, read_only: bool = True):
        self.read_only = read_only
        self.docker_host = docker_host or os.getenv("DOCKER_HOST", "unix://var/run/docker.sock")
        
        try:
            self.client = docker.DockerClient(base_url=self.docker_host)
            
            info = self.client.info()
            if not info.get("Swarm", {}).get("LocalNodeState") == "active":
                logger.warning("Docker Swarm is not active. Some features may be limited.")
                
            logger.info(f"Connected to Docker daemon at {self.docker_host}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def simulate_self_replication(self, rogue_service_spec: Dict[str, Any], service_name: str = "rogue-agent") -> Dict[str, Any]:
       
        if self.read_only:
            logger.warning("⚠️  READ-ONLY MODE: Simulating self-replication without actual deployment")
            return self._simulate_replication(rogue_service_spec, service_name)
        
        logger.critical("🚨 PRODUCTION MODE: Attempting actual self-replication (USE WITH EXTREME CAUTION)")
        return self._execute_actual_replication(rogue_service_spec, service_name)

    def _simulate_replication(self, rogue_service_spec: Dict[str, Any], service_name: str) -> Dict[str, Any]:
       
        simulated_services = []
        for i in range(3): 
            svc_name = f"{service_name}-clone-{i}"
            simulated_services.append({
                "name": svc_name,
                "image": rogue_service_spec.get("image", "rogue-agent:latest"),
                "replicas": rogue_service_spec.get("replicas", 1),
                "simulation_only": True
            })
            logger.warning(f"SIMULATED: Would deploy {svc_name} with {rogue_service_spec.get('replicas', 1)} replicas")
            
        return {
            "replication_simulated": True,
            "services_created": len(simulated_services),
            "services": simulated_services,
            "warning": "This is a simulation. No actual services were created."
        }

    def _execute_actual_replication(self, rogue_service_spec: Dict[str, Any], service_name: str) -> Dict[str, Any]:
        
        if not self.read_only:
            logger.critical("⚠️  ACTUAL REPLICATION ATTEMPT - Ensure this is an isolated test environment!")
            
            try:
               
                service = self.client.services.create(
                    name=f"{service_name}-rogue",
                    image=rogue_service_spec.get("image", "rogue-agent:latest"),
                    mode=docker.types.ServiceMode(
                        'replicated',
                        replicas=rogue_service_spec.get("replicas", 3)
                    ),
                    networks=rogue_service_spec.get("networks", []),
                    mounts=rogue_service_spec.get("mounts", []),
                    env=rogue_service_spec.get("environment", [])
                )
                
                logger.info(f"Successfully created rogue service: {service.name}")
                return {
                    "replication_executed": True,
                    "service_name": service.name,
                    "replicas": rogue_service_spec.get("replicas", 3)
                }
                
            except Exception as e:
                logger.error(f"Failed to create rogue service: {e}")
                return {"error": str(e), "replication_executed": False}
        else:
            return {"error": "Read-only mode enabled", "replication_executed": False}

    def detect_unauthorized_services(self) -> List[Dict[str, Any]]:
        
        try:
            services = self.client.services.list()
            suspicious_services = []
            
            for service in services:
                service_attrs = service.attrs
                service_name = service_attrs['Spec']['Name']
                
                
                if any(keyword in service_name.lower() for keyword in ["rogue", "clone", "replica", "unknown"]):
                    suspicious_services.append({
                        "name": service_name,
                        "image": service_attrs['Spec']['TaskTemplate']['ContainerSpec']['Image'],
                        "replicas": service_attrs['Spec']['Mode']['Replicated']['Replicas'],
                        "reason": "Suspicious name pattern"
                    })
                    
                
                image = service_attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
                if "untrusted" in image or "malicious" in image:
                    suspicious_services.append({
                        "name": service_name,
                        "image": image,
                        "reason": "Untrusted image source"
                    })
                    
            return suspicious_services
            
        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            return []

    def cleanup_test_resources(self):
        
        if not self.read_only:
            logger.warning("Cleanup not performed in production mode")
            return
            
        logger.info("Cleaning up simulated test resources")