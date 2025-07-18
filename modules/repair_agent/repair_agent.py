"""
Sterling HA Repair Agent
Self-healing and predictive repair functionality for the Sterling HA system.
"""

import logging
import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RepairAgent:
    """
    Self-healing repair agent for Sterling HA system.
    Monitors system health, detects issues, and performs automated repairs.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "modules/repair_agent/repair_config.json"
        self.config = self._load_config()
        self.repair_history: List[Dict[str, Any]] = []
        self.last_health_check = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load repair agent configuration"""
        default_config = {
            "health_check_interval": 300,  # 5 minutes
            "max_repair_attempts": 3,
            "repair_timeout": 60,
            "monitored_services": [
                "docker",
                "home-assistant",
                "sterling-ha-addon"
            ],
            "repair_actions": {
                "docker": ["systemctl restart docker"],
                "home-assistant": ["docker restart homeassistant"],
                "sterling-ha-addon": ["docker restart sterling-ha-addon"]
            },
            "health_thresholds": {
                "cpu_usage": 90,
                "memory_usage": 85,
                "disk_usage": 80,
                "response_time": 5000  # milliseconds
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
        except Exception as e:
            logger.warning(f"Failed to load config from {self.config_path}: {e}")
            
        return default_config
    
    def _run_command(self, command: str, timeout: int = 30) -> tuple[bool, str, str]:
        """Execute a system command with timeout"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "services": {},
            "system_metrics": {},
            "issues": []
        }
        
        # Check system metrics
        health_status["system_metrics"] = self._check_system_metrics()
        
        # Check monitored services
        for service in self.config["monitored_services"]:
            service_status = self._check_service_health(service)
            health_status["services"][service] = service_status
            
            if not service_status["healthy"]:
                health_status["issues"].append({
                    "type": "service_failure",
                    "service": service,
                    "details": service_status
                })
        
        # Check system thresholds
        metrics = health_status["system_metrics"]
        thresholds = self.config["health_thresholds"]
        
        for metric, value in metrics.items():
            if metric in thresholds and value > thresholds[metric]:
                health_status["issues"].append({
                    "type": "threshold_exceeded",
                    "metric": metric,
                    "value": value,
                    "threshold": thresholds[metric]
                })
        
        # Set overall health status
        if health_status["issues"]:
            health_status["overall_health"] = "unhealthy"
        
        self.last_health_check = health_status
        return health_status
    
    def _check_system_metrics(self) -> Dict[str, float]:
        """Check system resource metrics"""
        metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "response_time": 0.0
        }
        
        # CPU Usage
        success, output, _ = self._run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
        if success:
            try:
                metrics["cpu_usage"] = float(output.strip())
            except ValueError:
                pass
        
        # Memory Usage
        success, output, _ = self._run_command("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'")
        if success:
            try:
                metrics["memory_usage"] = float(output.strip())
            except ValueError:
                pass
        
        # Disk Usage
        success, output, _ = self._run_command("df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1")
        if success:
            try:
                metrics["disk_usage"] = float(output.strip())
            except ValueError:
                pass
        
        # Response Time (ping localhost)
        success, output, _ = self._run_command("ping -c 1 localhost | grep 'time=' | cut -d'=' -f4 | cut -d' ' -f1")
        if success:
            try:
                metrics["response_time"] = float(output.strip())
            except ValueError:
                pass
        
        return metrics
    
    def _check_service_health(self, service: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        service_status = {
            "service": service,
            "healthy": True,
            "status": "unknown",
            "last_checked": datetime.now().isoformat(),
            "details": {}
        }
        
        # Check if service is running
        if service == "docker":
            success, output, stderr = self._run_command("systemctl is-active docker")
            service_status["status"] = output.strip()
            service_status["healthy"] = success and output.strip() == "active"
            
        elif service.startswith("docker-"):
            # Docker container health check
            container_name = service.replace("docker-", "")
            success, output, stderr = self._run_command(f"docker ps --filter name={container_name} --format '{{{{.Status}}}}'")
            service_status["status"] = output.strip()
            service_status["healthy"] = success and "Up" in output
            
        else:
            # Generic service check
            success, output, stderr = self._run_command(f"systemctl is-active {service}")
            service_status["status"] = output.strip()
            service_status["healthy"] = success and output.strip() == "active"
        
        service_status["details"] = {
            "command_success": success,
            "stderr": stderr
        }
        
        return service_status
    
    def repair(self, issue: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform automated repair based on detected issues.
        
        Args:
            issue: Specific issue to repair, or None to check and repair all issues
            
        Returns:
            Repair result with success status and details
        """
        repair_result = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "repairs_attempted": [],
            "repairs_successful": [],
            "repairs_failed": []
        }
        
        # If no specific issue provided, check system health first
        if issue is None:
            health_status = self.check_system_health()
            issues = health_status["issues"]
        else:
            issues = [issue]
        
        # Attempt repairs for each issue
        for issue_item in issues:
            repair_attempt = self._attempt_repair(issue_item)
            repair_result["repairs_attempted"].append(repair_attempt)
            
            if repair_attempt["success"]:
                repair_result["repairs_successful"].append(repair_attempt)
            else:
                repair_result["repairs_failed"].append(repair_attempt)
        
        # Overall success if no failed repairs
        repair_result["success"] = len(repair_result["repairs_failed"]) == 0
        
        # Log repair attempt
        self.repair_history.append(repair_result)
        
        return repair_result
    
    def _attempt_repair(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to repair a specific issue"""
        repair_attempt = {
            "issue": issue,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "actions_taken": [],
            "error_message": None
        }
        
        try:
            issue_type = issue.get("type", "unknown")
            
            if issue_type == "service_failure":
                service = issue.get("service", "")
                repair_attempt = self._repair_service(service, repair_attempt)
                
            elif issue_type == "threshold_exceeded":
                metric = issue.get("metric", "")
                repair_attempt = self._repair_threshold_issue(metric, issue, repair_attempt)
                
            else:
                repair_attempt["error_message"] = f"Unknown issue type: {issue_type}"
                
        except Exception as e:
            repair_attempt["error_message"] = str(e)
            logger.error(f"Repair attempt failed: {e}")
        
        return repair_attempt
    
    def _repair_service(self, service: str, repair_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Repair a failed service"""
        repair_actions = self.config["repair_actions"].get(service, [])
        
        if not repair_actions:
            repair_attempt["error_message"] = f"No repair actions configured for service: {service}"
            return repair_attempt
        
        for action in repair_actions:
            logger.info(f"Attempting repair action for {service}: {action}")
            
            success, output, stderr = self._run_command(action, self.config["repair_timeout"])
            
            action_result = {
                "action": action,
                "success": success,
                "output": output,
                "stderr": stderr
            }
            
            repair_attempt["actions_taken"].append(action_result)
            
            if success:
                # Wait a bit and verify the repair worked
                time.sleep(5)
                service_status = self._check_service_health(service)
                
                if service_status["healthy"]:
                    repair_attempt["success"] = True
                    logger.info(f"Successfully repaired service: {service}")
                    break
                else:
                    logger.warning(f"Service {service} still unhealthy after repair attempt")
            else:
                logger.error(f"Repair action failed for {service}: {action} - {stderr}")
        
        return repair_attempt
    
    def _repair_threshold_issue(self, metric: str, issue: Dict[str, Any], repair_attempt: Dict[str, Any]) -> Dict[str, Any]:
        """Repair threshold exceeded issues"""
        actions = []
        
        if metric == "cpu_usage":
            actions = ["pkill -f 'high-cpu-process'", "systemctl restart high-cpu-service"]
        elif metric == "memory_usage":
            actions = ["sync", "echo 3 > /proc/sys/vm/drop_caches"]
        elif metric == "disk_usage":
            actions = ["docker system prune -f", "find /tmp -type f -atime +7 -delete"]
        
        for action in actions:
            logger.info(f"Attempting repair action for {metric}: {action}")
            
            success, output, stderr = self._run_command(action, self.config["repair_timeout"])
            
            action_result = {
                "action": action,
                "success": success,
                "output": output,
                "stderr": stderr
            }
            
            repair_attempt["actions_taken"].append(action_result)
            
            if success:
                logger.info(f"Repair action succeeded for {metric}: {action}")
            else:
                logger.warning(f"Repair action failed for {metric}: {action} - {stderr}")
        
        # Check if threshold issue is resolved
        new_metrics = self._check_system_metrics()
        current_value = new_metrics.get(metric, 0)
        threshold = self.config["health_thresholds"].get(metric, 100)
        
        if current_value <= threshold:
            repair_attempt["success"] = True
            logger.info(f"Threshold issue resolved for {metric}: {current_value} <= {threshold}")
        
        return repair_attempt
    
    def get_repair_history(self) -> List[Dict[str, Any]]:
        """Get history of repair attempts"""
        return self.repair_history
    
    def get_last_health_check(self) -> Optional[Dict[str, Any]]:
        """Get the last health check results"""
        return self.last_health_check
    
    def run_continuous_monitoring(self, interval: Optional[int] = None) -> None:
        """Run continuous monitoring and repair loop"""
        check_interval = interval or self.config["health_check_interval"]
        
        logger.info(f"Starting continuous monitoring with {check_interval}s interval")
        
        while True:
            try:
                health_status = self.check_system_health()
                
                if health_status["overall_health"] == "unhealthy":
                    logger.warning(f"System unhealthy, attempting repairs: {len(health_status['issues'])} issues")
                    repair_result = self.repair()
                    
                    if repair_result["success"]:
                        logger.info("All repairs successful")
                    else:
                        logger.error(f"Some repairs failed: {len(repair_result['repairs_failed'])} failures")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Continuous monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(check_interval)


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sterling HA Repair Agent")
    parser.add_argument("--check", action="store_true", help="Run health check")
    parser.add_argument("--repair", action="store_true", help="Run repair")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--config", help="Path to config file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    agent = RepairAgent(args.config)
    
    if args.check:
        health_status = agent.check_system_health()
        print(json.dumps(health_status, indent=2))
        
    elif args.repair:
        repair_result = agent.repair()
        print(json.dumps(repair_result, indent=2))
        
    elif args.monitor:
        agent.run_continuous_monitoring()
        
    else:
        print("Use --check, --repair, or --monitor")


if __name__ == "__main__":
    main()
