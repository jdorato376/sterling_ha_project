"""
Sterling HA Project - Repair Agent
Self-healing and predictive repair capabilities for Home Assistant infrastructure.
"""

import logging
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RepairAction:
    """Represents a repair action that can be taken."""
    id: str
    name: str
    description: str
    priority: int  # 1-5, where 1 is highest priority
    command: str
    rollback_command: Optional[str] = None
    requires_restart: bool = False
    
@dataclass
class SystemHealth:
    """Represents the health status of the system."""
    timestamp: datetime
    overall_health: float  # 0-1 score
    services: Dict[str, bool]
    metrics: Dict[str, float]
    issues: List[str]
    recommendations: List[RepairAction]

class RepairAgent:
    """Main repair agent class for system self-healing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.health_threshold = self.config.get('health_threshold', 0.7)
        self.repair_history = []
        self.enabled_repairs = self.config.get('enabled_repairs', [
            'restart_service',
            'clear_logs',
            'check_disk_space',
            'network_diagnostics'
        ])
        
    def check_system_health(self) -> SystemHealth:
        """Check overall system health and identify issues."""
        logger.info("Checking system health...")
        
        timestamp = datetime.now()
        services = self._check_services()
        metrics = self._collect_metrics()
        issues = self._identify_issues(services, metrics)
        recommendations = self._generate_recommendations(issues)
        
        # Calculate overall health score
        service_health = sum(services.values()) / len(services) if services else 1.0
        metric_health = self._calculate_metric_health(metrics)
        overall_health = (service_health + metric_health) / 2
        
        health_status = SystemHealth(
            timestamp=timestamp,
            overall_health=overall_health,
            services=services,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations
        )
        
        logger.info(f"System health score: {overall_health:.2f}")
        return health_status
        
    def _check_services(self) -> Dict[str, bool]:
        """Check status of critical services."""
        services = {}
        
        # Check Home Assistant service
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'home-assistant'],
                capture_output=True,
                text=True,
                timeout=10
            )
            services['home-assistant'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            services['home-assistant'] = False
            
        # Check Docker service (if applicable)
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'docker'],
                capture_output=True,
                text=True,
                timeout=10
            )
            services['docker'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            services['docker'] = False
            
        # Check network connectivity
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=10
            )
            services['network'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            services['network'] = False
            
        return services
        
    def _collect_metrics(self) -> Dict[str, float]:
        """Collect system metrics."""
        metrics = {}
        
        # CPU usage
        try:
            result = subprocess.run(
                ['top', '-bn1'],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse CPU usage from top output
            for line in result.stdout.split('\n'):
                if 'Cpu(s):' in line:
                    # Extract CPU usage percentage
                    # Look for pattern like "5.0%us," or "5.0%us"
                    parts = line.split()
                    for part in parts:
                        if '%us' in part:
                            try:
                                # Remove %us and any trailing comma
                                cpu_str = part.replace('%us', '').rstrip(',')
                                metrics['cpu_usage'] = float(cpu_str)
                                break
                            except ValueError:
                                pass
                    break
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            metrics['cpu_usage'] = 0.0
            
        # Memory usage
        try:
            result = subprocess.run(
                ['free', '-m'],
                capture_output=True,
                text=True,
                timeout=10
            )
            lines = result.stdout.split('\n')
            if len(lines) >= 2:
                mem_line = lines[1].split()
                if len(mem_line) >= 3:
                    total_mem = float(mem_line[1])
                    used_mem = float(mem_line[2])
                    metrics['memory_usage'] = (used_mem / total_mem) * 100
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            metrics['memory_usage'] = 0.0
            
        # Disk usage
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=10
            )
            lines = result.stdout.split('\n')
            if len(lines) >= 2:
                disk_line = lines[1].split()
                if len(disk_line) >= 5:
                    usage_str = disk_line[4]
                    if usage_str.endswith('%'):
                        metrics['disk_usage'] = float(usage_str[:-1])
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            metrics['disk_usage'] = 0.0
            
        return metrics
        
    def _identify_issues(self, services: Dict[str, bool], metrics: Dict[str, float]) -> List[str]:
        """Identify issues based on services and metrics."""
        issues = []
        
        # Check for service failures
        for service, status in services.items():
            if not status:
                issues.append(f"Service {service} is not running")
                
        # Check for high resource usage
        if metrics.get('cpu_usage', 0) > 80:
            issues.append(f"High CPU usage: {metrics['cpu_usage']:.1f}%")
            
        if metrics.get('memory_usage', 0) > 85:
            issues.append(f"High memory usage: {metrics['memory_usage']:.1f}%")
            
        if metrics.get('disk_usage', 0) > 90:
            issues.append(f"High disk usage: {metrics['disk_usage']:.1f}%")
            
        return issues
        
    def _generate_recommendations(self, issues: List[str]) -> List[RepairAction]:
        """Generate repair recommendations based on identified issues."""
        recommendations = []
        
        for issue in issues:
            if 'Service' in issue and 'not running' in issue:
                service_name = issue.split()[1]
                recommendations.append(RepairAction(
                    id=f"restart_{service_name}",
                    name=f"Restart {service_name}",
                    description=f"Restart the {service_name} service",
                    priority=1,
                    command=f"systemctl restart {service_name}",
                    requires_restart=True
                ))
                
            elif 'High CPU usage' in issue:
                recommendations.append(RepairAction(
                    id="cpu_optimization",
                    name="CPU Optimization",
                    description="Optimize CPU usage by restarting high-usage processes",
                    priority=2,
                    command="systemctl restart home-assistant",
                    requires_restart=True
                ))
                
            elif 'High memory usage' in issue:
                recommendations.append(RepairAction(
                    id="memory_cleanup",
                    name="Memory Cleanup",
                    description="Clear system caches and restart services",
                    priority=2,
                    command="sync && echo 3 > /proc/sys/vm/drop_caches",
                ))
                
            elif 'High disk usage' in issue:
                recommendations.append(RepairAction(
                    id="disk_cleanup",
                    name="Disk Cleanup",
                    description="Clean up temporary files and logs",
                    priority=3,
                    command="find /tmp -type f -atime +7 -delete && journalctl --vacuum-size=100M",
                ))
                
        return recommendations
        
    def _calculate_metric_health(self, metrics: Dict[str, float]) -> float:
        """Calculate health score based on system metrics."""
        if not metrics:
            return 1.0
            
        # Weight different metrics
        cpu_health = max(0, (100 - metrics.get('cpu_usage', 0)) / 100)
        memory_health = max(0, (100 - metrics.get('memory_usage', 0)) / 100)
        disk_health = max(0, (100 - metrics.get('disk_usage', 0)) / 100)
        
        # Weighted average
        return (cpu_health * 0.3 + memory_health * 0.4 + disk_health * 0.3)
        
    def repair(self, actions: Optional[List[RepairAction]] = None) -> Dict[str, Any]:
        """Execute repair actions."""
        if actions is None:
            # Get current health status and recommendations
            health_status = self.check_system_health()
            actions = health_status.recommendations
            
        results = {
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        logger.info(f"Starting repair process with {len(actions)} actions")
        
        for action in actions:
            if action.id not in self.enabled_repairs and not action.id.startswith('test_'):
                logger.info(f"Skipping disabled repair: {action.id}")
                continue
                
            try:
                logger.info(f"Executing repair action: {action.name}")
                
                # Execute the repair command
                result = subprocess.run(
                    action.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    results['actions_taken'].append({
                        'action': action.name,
                        'status': 'success',
                        'command': action.command,
                        'output': result.stdout[:500]  # Truncate output
                    })
                    results['success_count'] += 1
                    logger.info(f"Repair action '{action.name}' completed successfully")
                else:
                    results['actions_taken'].append({
                        'action': action.name,
                        'status': 'failed',
                        'command': action.command,
                        'error': result.stderr[:500]  # Truncate error
                    })
                    results['failure_count'] += 1
                    results['errors'].append(f"{action.name}: {result.stderr}")
                    logger.error(f"Repair action '{action.name}' failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                results['actions_taken'].append({
                    'action': action.name,
                    'status': 'timeout',
                    'command': action.command,
                    'error': 'Command timed out'
                })
                results['failure_count'] += 1
                results['errors'].append(f"{action.name}: Command timed out")
                logger.error(f"Repair action '{action.name}' timed out")
                
            except Exception as e:
                results['actions_taken'].append({
                    'action': action.name,
                    'status': 'error',
                    'command': action.command,
                    'error': str(e)
                })
                results['failure_count'] += 1
                results['errors'].append(f"{action.name}: {str(e)}")
                logger.error(f"Repair action '{action.name}' failed with exception: {e}")
                
        # Save repair history
        self.repair_history.append(results)
        
        # Keep only last 100 repair records
        if len(self.repair_history) > 100:
            self.repair_history = self.repair_history[-100:]
            
        logger.info(f"Repair process completed: {results['success_count']} successes, {results['failure_count']} failures")
        return results
        
    def get_repair_history(self) -> List[Dict[str, Any]]:
        """Get the repair history."""
        return self.repair_history
        
    def is_healthy(self) -> bool:
        """Check if the system is healthy."""
        health_status = self.check_system_health()
        return health_status.overall_health >= self.health_threshold
