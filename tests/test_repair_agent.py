"""
Test suite for Sterling HA Project Repair Agent
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
from datetime import datetime

from modules.repair_agent.repair_agent import RepairAgent, RepairAction, SystemHealth


class TestRepairAgent:
    """Test cases for RepairAgent class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.repair_agent = RepairAgent()
        
    def test_repair_agent_initialization(self):
        """Test RepairAgent initialization."""
        assert self.repair_agent.health_threshold == 0.7
        assert self.repair_agent.repair_history == []
        assert 'restart_service' in self.repair_agent.enabled_repairs
        
    def test_repair_agent_with_config(self):
        """Test RepairAgent initialization with custom config."""
        config = {
            'health_threshold': 0.8,
            'enabled_repairs': ['restart_service', 'clear_logs']
        }
        agent = RepairAgent(config)
        assert agent.health_threshold == 0.8
        assert agent.enabled_repairs == ['restart_service', 'clear_logs']
        
    @patch('subprocess.run')
    def test_check_services_healthy(self, mock_run):
        """Test service health checking with healthy services."""
        # Mock successful service checks
        mock_run.return_value = Mock(returncode=0)
        
        services = self.repair_agent._check_services()
        
        assert 'home-assistant' in services
        assert 'docker' in services
        assert 'network' in services
        assert all(services.values())  # All services should be healthy
        
    @patch('subprocess.run')
    def test_check_services_unhealthy(self, mock_run):
        """Test service health checking with unhealthy services."""
        # Mock failed service checks
        mock_run.return_value = Mock(returncode=1)
        
        services = self.repair_agent._check_services()
        
        assert 'home-assistant' in services
        assert 'docker' in services
        assert 'network' in services
        assert not any(services.values())  # All services should be unhealthy
        
    @patch('subprocess.run')
    def test_collect_metrics(self, mock_run):
        """Test metric collection."""
        # Mock top command output
        top_output = "Cpu(s):  5.0%us,  2.0%sy,  0.0%ni, 93.0%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st"
        free_output = "             total       used       free     shared    buffers     cached\nMem:          2048       1024       1024          0          0          0"
        df_output = "Filesystem     Size  Used Avail Use% Mounted on\n/dev/sda1       10G  3.0G  7.0G  30% /"
        
        mock_run.side_effect = [
            Mock(returncode=0, stdout=top_output),
            Mock(returncode=0, stdout=free_output),
            Mock(returncode=0, stdout=df_output)
        ]
        
        metrics = self.repair_agent._collect_metrics()
        
        assert 'cpu_usage' in metrics
        assert 'memory_usage' in metrics
        assert 'disk_usage' in metrics
        assert metrics['cpu_usage'] == 5.0
        assert metrics['memory_usage'] == 50.0  # 1024/2048 * 100
        assert metrics['disk_usage'] == 30.0
        
    def test_identify_issues_with_service_failures(self):
        """Test issue identification with service failures."""
        services = {'home-assistant': False, 'docker': True, 'network': True}
        metrics = {'cpu_usage': 10.0, 'memory_usage': 20.0, 'disk_usage': 30.0}
        
        issues = self.repair_agent._identify_issues(services, metrics)
        
        assert len(issues) == 1
        assert 'Service home-assistant is not running' in issues
        
    def test_identify_issues_with_high_resource_usage(self):
        """Test issue identification with high resource usage."""
        services = {'home-assistant': True, 'docker': True, 'network': True}
        metrics = {'cpu_usage': 85.0, 'memory_usage': 90.0, 'disk_usage': 95.0}
        
        issues = self.repair_agent._identify_issues(services, metrics)
        
        assert len(issues) == 3
        assert any('High CPU usage' in issue for issue in issues)
        assert any('High memory usage' in issue for issue in issues)
        assert any('High disk usage' in issue for issue in issues)
        
    def test_generate_recommendations_for_service_failure(self):
        """Test recommendation generation for service failures."""
        issues = ['Service home-assistant is not running']
        
        recommendations = self.repair_agent._generate_recommendations(issues)
        
        assert len(recommendations) == 1
        assert recommendations[0].id == 'restart_home-assistant'
        assert recommendations[0].name == 'Restart home-assistant'
        assert recommendations[0].priority == 1
        assert 'systemctl restart home-assistant' in recommendations[0].command
        
    def test_generate_recommendations_for_resource_issues(self):
        """Test recommendation generation for resource issues."""
        issues = [
            'High CPU usage: 85.0%',
            'High memory usage: 90.0%',
            'High disk usage: 95.0%'
        ]
        
        recommendations = self.repair_agent._generate_recommendations(issues)
        
        assert len(recommendations) == 3
        assert any(rec.id == 'cpu_optimization' for rec in recommendations)
        assert any(rec.id == 'memory_cleanup' for rec in recommendations)
        assert any(rec.id == 'disk_cleanup' for rec in recommendations)
        
    def test_calculate_metric_health_perfect(self):
        """Test metric health calculation with perfect metrics."""
        metrics = {'cpu_usage': 0.0, 'memory_usage': 0.0, 'disk_usage': 0.0}
        
        health = self.repair_agent._calculate_metric_health(metrics)
        
        assert health == 1.0
        
    def test_calculate_metric_health_poor(self):
        """Test metric health calculation with poor metrics."""
        metrics = {'cpu_usage': 100.0, 'memory_usage': 100.0, 'disk_usage': 100.0}
        
        health = self.repair_agent._calculate_metric_health(metrics)
        
        assert health == 0.0
        
    def test_calculate_metric_health_empty(self):
        """Test metric health calculation with empty metrics."""
        metrics = {}
        
        health = self.repair_agent._calculate_metric_health(metrics)
        
        assert health == 1.0
        
    @patch('subprocess.run')
    def test_repair_success(self, mock_run):
        """Test successful repair execution."""
        # Mock successful command execution
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        actions = [
            RepairAction(
                id="test_action",
                name="Test Action",
                description="Test repair action",
                priority=1,
                command="echo 'test'"
            )
        ]
        
        results = self.repair_agent.repair(actions)
        
        assert results['success_count'] == 1
        assert results['failure_count'] == 0
        assert len(results['actions_taken']) == 1
        assert results['actions_taken'][0]['status'] == 'success'
        
    @patch('subprocess.run')
    def test_repair_failure(self, mock_run):
        """Test repair execution with failure."""
        # Mock failed command execution
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error occurred")
        
        actions = [
            RepairAction(
                id="test_action",
                name="Test Action",
                description="Test repair action",
                priority=1,
                command="false"
            )
        ]
        
        results = self.repair_agent.repair(actions)
        
        assert results['success_count'] == 0
        assert results['failure_count'] == 1
        assert len(results['actions_taken']) == 1
        assert results['actions_taken'][0]['status'] == 'failed'
        
    @patch('subprocess.run')
    def test_repair_timeout(self, mock_run):
        """Test repair execution with timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 60)
        
        actions = [
            RepairAction(
                id="test_action",
                name="Test Action",
                description="Test repair action",
                priority=1,
                command="sleep 120"
            )
        ]
        
        results = self.repair_agent.repair(actions)
        
        assert results['success_count'] == 0
        assert results['failure_count'] == 1
        assert len(results['actions_taken']) == 1
        assert results['actions_taken'][0]['status'] == 'timeout'
        
    @patch.object(RepairAgent, 'check_system_health')
    def test_is_healthy_true(self, mock_check):
        """Test is_healthy method when system is healthy."""
        mock_health = Mock()
        mock_health.overall_health = 0.8
        mock_check.return_value = mock_health
        
        assert self.repair_agent.is_healthy() is True
        
    @patch.object(RepairAgent, 'check_system_health')
    def test_is_healthy_false(self, mock_check):
        """Test is_healthy method when system is unhealthy."""
        mock_health = Mock()
        mock_health.overall_health = 0.5
        mock_check.return_value = mock_health
        
        assert self.repair_agent.is_healthy() is False
        
    def test_repair_history_tracking(self):
        """Test repair history tracking."""
        initial_history_length = len(self.repair_agent.repair_history)
        
        # Mock a repair action
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
            
            actions = [
                RepairAction(
                    id="test_action",
                    name="Test Action",
                    description="Test repair action",
                    priority=1,
                    command="echo 'test'"
                )
            ]
            
            self.repair_agent.repair(actions)
            
        assert len(self.repair_agent.repair_history) == initial_history_length + 1
        
    def test_get_repair_history(self):
        """Test getting repair history."""
        history = self.repair_agent.get_repair_history()
        assert isinstance(history, list)
        assert history == self.repair_agent.repair_history


class TestRepairAction:
    """Test cases for RepairAction dataclass."""
    
    def test_repair_action_creation(self):
        """Test RepairAction creation."""
        action = RepairAction(
            id="test_action",
            name="Test Action",
            description="Test repair action",
            priority=1,
            command="echo 'test'"
        )
        
        assert action.id == "test_action"
        assert action.name == "Test Action"
        assert action.description == "Test repair action"
        assert action.priority == 1
        assert action.command == "echo 'test'"
        assert action.rollback_command is None
        assert action.requires_restart is False
        
    def test_repair_action_with_rollback(self):
        """Test RepairAction with rollback command."""
        action = RepairAction(
            id="test_action",
            name="Test Action",
            description="Test repair action",
            priority=1,
            command="systemctl stop service",
            rollback_command="systemctl start service",
            requires_restart=True
        )
        
        assert action.rollback_command == "systemctl start service"
        assert action.requires_restart is True


class TestSystemHealth:
    """Test cases for SystemHealth dataclass."""
    
    def test_system_health_creation(self):
        """Test SystemHealth creation."""
        timestamp = datetime.now()
        services = {'home-assistant': True, 'docker': True}
        metrics = {'cpu_usage': 10.0, 'memory_usage': 20.0}
        issues = ['Test issue']
        recommendations = []
        
        health = SystemHealth(
            timestamp=timestamp,
            overall_health=0.8,
            services=services,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations
        )
        
        assert health.timestamp == timestamp
        assert health.overall_health == 0.8
        assert health.services == services
        assert health.metrics == metrics
        assert health.issues == issues
        assert health.recommendations == recommendations