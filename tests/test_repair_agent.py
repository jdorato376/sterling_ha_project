"""
Tests for Sterling HA Repair Agent
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from modules.repair_agent.repair_agent import RepairAgent


class TestRepairAgent:
    """Test cases for RepairAgent class"""
    
    def test_initialization(self):
        """Test RepairAgent initialization"""
        agent = RepairAgent()
        assert agent.config is not None
        assert agent.repair_history == []
        assert agent.last_health_check is None
        
    def test_load_config_default(self):
        """Test loading default configuration"""
        agent = RepairAgent()
        config = agent.config
        
        assert "health_check_interval" in config
        assert "max_repair_attempts" in config
        assert "monitored_services" in config
        assert "repair_actions" in config
        assert "health_thresholds" in config
        
    def test_load_config_custom(self):
        """Test loading custom configuration"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_config = {
                "health_check_interval": 600,
                "monitored_services": ["custom-service"]
            }
            json.dump(custom_config, f)
            config_path = f.name
        
        try:
            agent = RepairAgent(config_path)
            assert agent.config["health_check_interval"] == 600
            assert "custom-service" in agent.config["monitored_services"]
        finally:
            Path(config_path).unlink()
    
    @patch('modules.repair_agent.repair_agent.subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_run.return_value = Mock(returncode=0, stdout="success", stderr="")
        
        agent = RepairAgent()
        success, stdout, stderr = agent._run_command("echo test")
        
        assert success is True
        assert stdout == "success"
        assert stderr == ""
        
    @patch('modules.repair_agent.repair_agent.subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test failed command execution"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
        
        agent = RepairAgent()
        success, stdout, stderr = agent._run_command("false")
        
        assert success is False
        assert stdout == ""
        assert stderr == "error"
    
    @patch('modules.repair_agent.repair_agent.subprocess.run')
    def test_check_system_metrics(self, mock_run):
        """Test system metrics checking"""
        # Mock different command outputs
        def mock_run_side_effect(command, **kwargs):
            if "top" in command:
                return Mock(returncode=0, stdout="15.2\n", stderr="")
            elif "free" in command:
                return Mock(returncode=0, stdout="75.3", stderr="")
            elif "df" in command:
                return Mock(returncode=0, stdout="45", stderr="")
            elif "ping" in command:
                return Mock(returncode=0, stdout="2.5", stderr="")
            else:
                return Mock(returncode=1, stdout="", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        agent = RepairAgent()
        metrics = agent._check_system_metrics()
        
        assert metrics["cpu_usage"] == 15.2
        assert metrics["memory_usage"] == 75.3
        assert metrics["disk_usage"] == 45.0
        assert metrics["response_time"] == 2.5
    
    @patch('modules.repair_agent.repair_agent.subprocess.run')
    def test_check_service_health_docker(self, mock_run):
        """Test Docker service health check"""
        mock_run.return_value = Mock(returncode=0, stdout="active\n", stderr="")
        
        agent = RepairAgent()
        status = agent._check_service_health("docker")
        
        assert status["service"] == "docker"
        assert status["healthy"] is True
        assert status["status"] == "active"
    
    @patch('modules.repair_agent.repair_agent.subprocess.run')
    def test_check_service_health_container(self, mock_run):
        """Test container health check"""
        mock_run.return_value = Mock(returncode=0, stdout="Up 2 hours\n", stderr="")
        
        agent = RepairAgent()
        status = agent._check_service_health("docker-homeassistant")
        
        assert status["service"] == "docker-homeassistant"
        assert status["healthy"] is True
        assert "Up" in status["status"]
    
    @patch.object(RepairAgent, '_check_system_metrics')
    @patch.object(RepairAgent, '_check_service_health')
    def test_check_system_health_healthy(self, mock_check_service, mock_check_metrics):
        """Test system health check when system is healthy"""
        mock_check_metrics.return_value = {
            "cpu_usage": 50.0,
            "memory_usage": 60.0,
            "disk_usage": 40.0,
            "response_time": 2.0
        }
        mock_check_service.return_value = {
            "service": "docker",
            "healthy": True,
            "status": "active"
        }
        
        agent = RepairAgent()
        health_status = agent.check_system_health()
        
        assert health_status["overall_health"] == "healthy"
        assert len(health_status["issues"]) == 0
    
    @patch.object(RepairAgent, '_check_system_metrics')
    @patch.object(RepairAgent, '_check_service_health')
    def test_check_system_health_unhealthy(self, mock_check_service, mock_check_metrics):
        """Test system health check when system is unhealthy"""
        mock_check_metrics.return_value = {
            "cpu_usage": 95.0,  # Above threshold
            "memory_usage": 60.0,
            "disk_usage": 40.0,
            "response_time": 2.0
        }
        mock_check_service.return_value = {
            "service": "docker",
            "healthy": False,
            "status": "failed"
        }
        
        agent = RepairAgent()
        health_status = agent.check_system_health()
        
        assert health_status["overall_health"] == "unhealthy"
        # Should have 3 service failures (docker, home-assistant, sterling-ha-addon) + 1 CPU threshold
        assert len(health_status["issues"]) == 4
    
    @patch.object(RepairAgent, '_run_command')
    @patch.object(RepairAgent, '_check_service_health')
    def test_repair_service_success(self, mock_check_service, mock_run_command):
        """Test successful service repair"""
        # Mock the repair command to succeed
        mock_run_command.return_value = (True, "success", "")
        
        # Mock service health check to return healthy after repair
        mock_check_service.return_value = {
            "service": "docker", 
            "healthy": True, 
            "status": "active"
        }
        
        agent = RepairAgent()
        issue = {
            "type": "service_failure",
            "service": "docker"
        }
        
        repair_result = agent._attempt_repair(issue)
        
        assert repair_result["success"] is True
        assert len(repair_result["actions_taken"]) > 0
    
    @patch.object(RepairAgent, '_run_command')
    def test_repair_threshold_issue(self, mock_run_command):
        """Test repair of threshold exceeded issue"""
        mock_run_command.return_value = (True, "success", "")
        
        agent = RepairAgent()
        issue = {
            "type": "threshold_exceeded",
            "metric": "memory_usage",
            "value": 90.0,
            "threshold": 85.0
        }
        
        with patch.object(agent, '_check_system_metrics') as mock_metrics:
            mock_metrics.return_value = {"memory_usage": 70.0}  # Below threshold after repair
            
            repair_result = agent._attempt_repair(issue)
            
            assert repair_result["success"] is True
            assert len(repair_result["actions_taken"]) > 0
    
    @patch.object(RepairAgent, 'check_system_health')
    @patch.object(RepairAgent, '_attempt_repair')
    def test_repair_with_issues(self, mock_attempt_repair, mock_check_health):
        """Test repair method with detected issues"""
        mock_check_health.return_value = {
            "overall_health": "unhealthy",
            "issues": [
                {"type": "service_failure", "service": "docker"},
                {"type": "threshold_exceeded", "metric": "cpu_usage"}
            ]
        }
        mock_attempt_repair.return_value = {"success": True}
        
        agent = RepairAgent()
        repair_result = agent.repair()
        
        assert repair_result["success"] is True
        assert len(repair_result["repairs_attempted"]) == 2
        assert len(repair_result["repairs_successful"]) == 2
        assert len(repair_result["repairs_failed"]) == 0
    
    def test_repair_history_tracking(self):
        """Test that repair history is properly tracked"""
        agent = RepairAgent()
        
        # Mock a repair result
        with patch.object(agent, 'check_system_health') as mock_health:
            mock_health.return_value = {"overall_health": "healthy", "issues": []}
            
            repair_result = agent.repair()
            
            assert len(agent.repair_history) == 1
            assert agent.repair_history[0]["success"] is True
    
    def test_get_repair_history(self):
        """Test getting repair history"""
        agent = RepairAgent()
        
        # Add some mock history
        agent.repair_history = [
            {"timestamp": "2023-01-01T10:00:00", "success": True},
            {"timestamp": "2023-01-01T11:00:00", "success": False}
        ]
        
        history = agent.get_repair_history()
        
        assert len(history) == 2
        assert history[0]["success"] is True
        assert history[1]["success"] is False
    
    def test_get_last_health_check(self):
        """Test getting last health check results"""
        agent = RepairAgent()
        
        # Initially None
        assert agent.get_last_health_check() is None
        
        # After health check
        with patch.object(agent, '_check_system_metrics') as mock_metrics:
            mock_metrics.return_value = {"cpu_usage": 50.0}
            
            with patch.object(agent, '_check_service_health') as mock_service:
                mock_service.return_value = {"service": "docker", "healthy": True}
                
                health_status = agent.check_system_health()
                
                assert agent.get_last_health_check() == health_status
    
    def test_unknown_issue_type(self):
        """Test handling of unknown issue types"""
        agent = RepairAgent()
        
        issue = {
            "type": "unknown_issue",
            "details": "something went wrong"
        }
        
        repair_result = agent._attempt_repair(issue)
        
        assert repair_result["success"] is False
        assert "Unknown issue type" in repair_result["error_message"]


if __name__ == "__main__":
    pytest.main([__file__])