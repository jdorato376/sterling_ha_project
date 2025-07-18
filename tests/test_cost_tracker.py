"""
Tests for Sterling HA Cost Tracker
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from modules.cost_tracker.cost_tracker import CostTracker, check_cost


class TestCostTracker:
    """Test cases for CostTracker class"""
    
    def test_initialization(self):
        """Test CostTracker initialization"""
        tracker = CostTracker()
        assert tracker.config is not None
        assert tracker.cost_history == []
        assert tracker.bigquery_client is None  # Without credentials
        assert tracker.monitoring_client is None  # Without credentials
        
    def test_initialization_with_project_id(self):
        """Test CostTracker initialization with project ID"""
        tracker = CostTracker(project_id="test-project")
        assert tracker.project_id == "test-project"
        
    def test_load_config_default(self):
        """Test loading default configuration"""
        tracker = CostTracker()
        config = tracker.config
        
        assert "daily_cost_threshold" in config
        assert "monthly_cost_threshold" in config
        assert "cost_check_interval" in config
        assert "alert_channels" in config
        assert "tracked_services" in config
        assert "billing_export_table" in config
        assert "cost_optimization" in config
        
    def test_load_config_custom(self):
        """Test loading custom configuration"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            custom_config = {
                "daily_cost_threshold": 5.0,
                "monthly_cost_threshold": 100.0,
                "tracked_services": ["custom.service.com"]
            }
            json.dump(custom_config, f)
            config_path = f.name
        
        try:
            tracker = CostTracker(config_path=config_path)
            assert tracker.config["daily_cost_threshold"] == 5.0
            assert tracker.config["monthly_cost_threshold"] == 100.0
            assert "custom.service.com" in tracker.config["tracked_services"]
        finally:
            Path(config_path).unlink()
    
    @patch('random.uniform')
    def test_get_mock_costs(self, mock_random):
        """Test mock cost generation"""
        mock_random.return_value = 0.25
        
        tracker = CostTracker()
        cost_data = {
            "date": "2023-01-01",
            "total_cost": 0.0,
            "service_costs": {}
        }
        
        result = tracker._get_mock_costs(cost_data)
        
        assert result["total_cost"] > 0
        assert len(result["service_costs"]) > 0
        assert all(cost > 0 for cost in result["service_costs"].values())
    
    @patch('random.uniform')
    def test_get_mock_monthly_costs(self, mock_random):
        """Test mock monthly cost generation"""
        mock_random.return_value = 10.0
        
        tracker = CostTracker()
        cost_data = {
            "month": "2023-01",
            "total_cost": 0.0,
            "service_costs": {}
        }
        
        result = tracker._get_mock_monthly_costs(cost_data)
        
        assert result["total_cost"] > 0
        assert len(result["service_costs"]) > 0
        assert all(cost > 0 for cost in result["service_costs"].values())
    
    @patch.object(CostTracker, '_get_mock_costs')
    @patch.object(CostTracker, '_send_cost_alert')
    def test_check_daily_costs_below_threshold(self, mock_send_alert, mock_get_costs):
        """Test daily cost check when below threshold"""
        mock_get_costs.return_value = {
            "date": "2023-01-01",
            "total_cost": 1.0,
            "service_costs": {"compute": 0.5, "storage": 0.5},
            "threshold_exceeded": False,
            "alert_sent": False
        }
        
        tracker = CostTracker()
        result = tracker.check_daily_costs()
        
        assert result["total_cost"] == 1.0
        assert result["threshold_exceeded"] is False
        assert result["alert_sent"] is False
        assert len(tracker.cost_history) == 1
        mock_send_alert.assert_not_called()
    
    @patch.object(CostTracker, '_get_mock_costs')
    @patch.object(CostTracker, '_send_cost_alert')
    def test_check_daily_costs_above_threshold(self, mock_send_alert, mock_get_costs):
        """Test daily cost check when above threshold"""
        mock_get_costs.return_value = {
            "date": "2023-01-01",
            "total_cost": 5.0,
            "service_costs": {"compute": 3.0, "storage": 2.0},
            "threshold_exceeded": False,
            "alert_sent": False
        }
        mock_send_alert.return_value = True
        
        tracker = CostTracker()
        result = tracker.check_daily_costs()
        
        assert result["total_cost"] == 5.0
        assert result["threshold_exceeded"] is True
        assert result["alert_sent"] is True
        mock_send_alert.assert_called_once()
    
    @patch.object(CostTracker, '_get_mock_monthly_costs')
    @patch.object(CostTracker, '_send_cost_alert')
    def test_check_monthly_costs_below_threshold(self, mock_send_alert, mock_get_costs):
        """Test monthly cost check when below threshold"""
        mock_get_costs.return_value = {
            "month": "2023-01",
            "total_cost": 30.0,
            "service_costs": {"compute": 15.0, "storage": 15.0},
            "threshold_exceeded": False,
            "alert_sent": False
        }
        
        tracker = CostTracker()
        result = tracker.check_monthly_costs()
        
        assert result["total_cost"] == 30.0
        assert result["threshold_exceeded"] is False
        assert result["alert_sent"] is False
        mock_send_alert.assert_not_called()
    
    @patch.object(CostTracker, '_get_mock_monthly_costs')
    @patch.object(CostTracker, '_send_cost_alert')
    def test_check_monthly_costs_above_threshold(self, mock_send_alert, mock_get_costs):
        """Test monthly cost check when above threshold"""
        mock_get_costs.return_value = {
            "month": "2023-01",
            "total_cost": 75.0,
            "service_costs": {"compute": 40.0, "storage": 35.0},
            "threshold_exceeded": False,
            "alert_sent": False
        }
        mock_send_alert.return_value = True
        
        tracker = CostTracker()
        result = tracker.check_monthly_costs()
        
        assert result["total_cost"] == 75.0
        assert result["threshold_exceeded"] is True
        assert result["alert_sent"] is True
        mock_send_alert.assert_called_once()
    
    def test_format_alert_message(self):
        """Test alert message formatting"""
        tracker = CostTracker()
        cost_data = {
            "date": "2023-01-01",
            "total_cost": 5.0,
            "service_costs": {
                "compute": 3.0,
                "storage": 1.5,
                "network": 0.5
            }
        }
        
        message = tracker._format_alert_message(cost_data, "daily")
        
        assert "Daily Threshold Exceeded" in message
        assert "$5.00" in message
        assert "$2.00" in message  # default daily threshold
        assert "compute: $3.00" in message
        assert "storage: $1.50" in message
        assert "network: $0.50" in message
    
    def test_send_email_alert(self):
        """Test email alert sending (placeholder)"""
        tracker = CostTracker()
        result = tracker._send_email_alert("test message")
        assert result is True
    
    def test_send_slack_alert(self):
        """Test Slack alert sending (placeholder)"""
        tracker = CostTracker()
        result = tracker._send_slack_alert("test message")
        assert result is True
    
    def test_send_sms_alert(self):
        """Test SMS alert sending (placeholder)"""
        tracker = CostTracker()
        result = tracker._send_sms_alert("test message")
        assert result is True
    
    @patch.object(CostTracker, '_send_email_alert')
    @patch.object(CostTracker, '_send_slack_alert')
    @patch.object(CostTracker, '_send_sms_alert')
    def test_send_cost_alert_all_channels(self, mock_sms, mock_slack, mock_email):
        """Test sending cost alert to all channels"""
        mock_email.return_value = True
        mock_slack.return_value = True
        mock_sms.return_value = True
        
        tracker = CostTracker()
        tracker.config["alert_channels"] = {
            "email": "test@example.com",
            "slack_webhook": "https://hooks.slack.com/...",
            "sms_number": "+1234567890"
        }
        
        cost_data = {
            "total_cost": 5.0,
            "service_costs": {"compute": 3.0, "storage": 2.0}
        }
        
        result = tracker._send_cost_alert(cost_data, "daily")
        
        assert result is True
        mock_email.assert_called_once()
        mock_slack.assert_called_once()
        mock_sms.assert_called_once()
    
    @patch.object(CostTracker, '_find_idle_vms')
    @patch.object(CostTracker, '_find_old_builds')
    def test_get_cost_recommendations(self, mock_find_builds, mock_find_vms):
        """Test cost optimization recommendations"""
        mock_find_vms.return_value = [
            {"name": "vm1", "idle_hours": 3},
            {"name": "vm2", "idle_hours": 5}
        ]
        mock_find_builds.return_value = [
            {"build_id": "build1", "age_days": 45},
            {"build_id": "build2", "age_days": 60}
        ]
        
        tracker = CostTracker()
        recommendations = tracker.get_cost_recommendations()
        
        assert len(recommendations) == 2
        assert any(rec["type"] == "idle_vm_shutdown" for rec in recommendations)
        assert any(rec["type"] == "cleanup_old_builds" for rec in recommendations)
    
    @patch.object(CostTracker, '_shutdown_idle_vms')
    @patch.object(CostTracker, '_cleanup_old_builds')
    @patch.object(CostTracker, 'get_cost_recommendations')
    def test_optimize_costs(self, mock_get_recommendations, mock_cleanup, mock_shutdown):
        """Test cost optimization execution"""
        mock_get_recommendations.return_value = [
            {
                "type": "idle_vm_shutdown",
                "action": "shutdown_idle_vms",
                "details": [{"name": "vm1"}]
            },
            {
                "type": "cleanup_old_builds",
                "action": "cleanup_old_builds",
                "details": [{"build_id": "build1"}]
            }
        ]
        
        mock_shutdown.return_value = {"action": "shutdown_idle_vms", "savings": 0.5, "success": True}
        mock_cleanup.return_value = {"action": "cleanup_old_builds", "savings": 0.1, "success": True}
        
        tracker = CostTracker()
        result = tracker.optimize_costs()
        
        assert result["total_savings"] == 0.6
        assert len(result["actions_taken"]) == 2
        assert len(result["errors"]) == 0
        mock_shutdown.assert_called_once()
        mock_cleanup.assert_called_once()
    
    def test_calculate_vm_savings(self):
        """Test VM savings calculation"""
        tracker = CostTracker()
        idle_vms = [{"name": "vm1"}, {"name": "vm2"}, {"name": "vm3"}]
        
        savings = tracker._calculate_vm_savings(idle_vms)
        
        assert savings == 1.5  # 3 VMs * $0.50 each
    
    def test_calculate_build_savings(self):
        """Test build cleanup savings calculation"""
        tracker = CostTracker()
        old_builds = [{"build_id": "build1"}, {"build_id": "build2"}]
        
        savings = tracker._calculate_build_savings(old_builds)
        
        assert savings == 0.2  # 2 builds * $0.10 each
    
    def test_get_cost_history(self):
        """Test getting cost history"""
        tracker = CostTracker()
        
        # Add some mock history
        tracker.cost_history = [
            {"date": "2023-01-01", "total_cost": 1.0},
            {"date": "2023-01-02", "total_cost": 2.0}
        ]
        
        history = tracker.get_cost_history()
        
        assert len(history) == 2
        assert history[0]["total_cost"] == 1.0
        assert history[1]["total_cost"] == 2.0
    
    @patch.object(CostTracker, 'check_daily_costs')
    @patch.object(CostTracker, 'check_monthly_costs')
    @patch.object(CostTracker, 'get_cost_recommendations')
    def test_export_cost_report(self, mock_recommendations, mock_monthly, mock_daily):
        """Test cost report export"""
        mock_daily.return_value = {"total_cost": 1.0, "date": "2023-01-01"}
        mock_monthly.return_value = {"total_cost": 25.0, "month": "2023-01"}
        mock_recommendations.return_value = [{"type": "test_recommendation"}]
        
        tracker = CostTracker()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = tracker.export_cost_report(output_path)
            
            assert result_path == output_path
            assert Path(output_path).exists()
            
            # Verify report content
            with open(output_path, 'r') as f:
                report_data = json.load(f)
            
            assert "generated_at" in report_data
            assert "daily_costs" in report_data
            assert "monthly_costs" in report_data
            assert "recommendations" in report_data
            assert "cost_history" in report_data
            
        finally:
            Path(output_path).unlink()
    
    def test_error_handling_in_daily_costs(self):
        """Test error handling in daily cost check"""
        tracker = CostTracker()
        
        with patch.object(tracker, '_get_mock_costs') as mock_get_costs:
            mock_get_costs.side_effect = Exception("Test error")
            
            result = tracker.check_daily_costs()
            
            assert result["error"] == "Test error"
            assert result["total_cost"] == 0.0
    
    def test_error_handling_in_monthly_costs(self):
        """Test error handling in monthly cost check"""
        tracker = CostTracker()
        
        with patch.object(tracker, '_get_mock_monthly_costs') as mock_get_costs:
            mock_get_costs.side_effect = Exception("Test error")
            
            result = tracker.check_monthly_costs()
            
            assert result["error"] == "Test error"
            assert result["total_cost"] == 0.0


class TestCheckCostFunction:
    """Test the standalone check_cost function"""
    
    @patch('modules.cost_tracker.cost_tracker.CostTracker')
    def test_check_cost_below_threshold(self, mock_tracker_class):
        """Test check_cost function when below threshold"""
        mock_tracker = Mock()
        mock_tracker.check_daily_costs.return_value = {
            "threshold_exceeded": False,
            "total_cost": 1.0
        }
        mock_tracker_class.return_value = mock_tracker
        
        result = check_cost()
        
        assert result is True
        mock_tracker.check_daily_costs.assert_called_once()
    
    @patch('modules.cost_tracker.cost_tracker.CostTracker')
    def test_check_cost_above_threshold(self, mock_tracker_class):
        """Test check_cost function when above threshold"""
        mock_tracker = Mock()
        mock_tracker.check_daily_costs.return_value = {
            "threshold_exceeded": True,
            "total_cost": 5.0
        }
        mock_tracker_class.return_value = mock_tracker
        
        result = check_cost()
        
        assert result is False
        mock_tracker.check_daily_costs.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])