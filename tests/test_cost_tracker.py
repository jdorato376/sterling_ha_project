"""
Test suite for Sterling HA Project Cost Tracker
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from datetime import datetime, timedelta

from modules.cost_tracker.cost_tracker import CostTracker, CostData, CostAlert, check_cost


class TestCostTracker:
    """Test cases for CostTracker class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.cost_tracker = CostTracker()
        
    def test_cost_tracker_initialization(self):
        """Test CostTracker initialization."""
        assert self.cost_tracker.alert_threshold == 2.0
        assert self.cost_tracker.cost_history == []
        assert self.cost_tracker.alert_config.threshold_usd == 2.0
        assert self.cost_tracker.alert_config.period_days == 1
        assert self.cost_tracker.alert_config.enabled is True
        
    def test_cost_tracker_with_config(self):
        """Test CostTracker initialization with custom config."""
        config = {
            'project_id': 'test-project',
            'alert_threshold': 5.0,
            'alert_channels': ['email', 'slack'],
            'alerts_enabled': False
        }
        
        tracker = CostTracker(config)
        assert tracker.project_id == 'test-project'
        assert tracker.alert_threshold == 5.0
        assert tracker.alert_config.threshold_usd == 5.0
        assert tracker.alert_config.alert_channels == ['email', 'slack']
        assert tracker.alert_config.enabled is False
        
    def test_should_alert_under_threshold(self):
        """Test alert logic when cost is under threshold."""
        total_cost = 1.5
        days = 1
        
        should_alert = self.cost_tracker._should_alert(total_cost, days)
        assert should_alert is False
        
    def test_should_alert_over_threshold(self):
        """Test alert logic when cost is over threshold."""
        total_cost = 3.0
        days = 1
        
        should_alert = self.cost_tracker._should_alert(total_cost, days)
        assert should_alert is True
        
    def test_should_alert_multi_day_threshold(self):
        """Test alert logic for multi-day periods."""
        total_cost = 5.0
        days = 3
        # Threshold is 2.0 * 3 = 6.0, so 5.0 should not trigger
        
        should_alert = self.cost_tracker._should_alert(total_cost, days)
        assert should_alert is False
        
        total_cost = 7.0
        should_alert = self.cost_tracker._should_alert(total_cost, days)
        assert should_alert is True
        
    def test_create_cost_summary_empty(self):
        """Test cost summary creation with empty data."""
        cost_data = []
        days = 1
        
        summary = self.cost_tracker._create_cost_summary(cost_data, days)
        
        assert summary['success'] is True
        assert summary['period_days'] == 1
        assert summary['total_cost_usd'] == 0.0
        assert summary['threshold_usd'] == 2.0
        assert summary['alert_triggered'] is False
        assert summary['cost_breakdown'] == []
        assert summary['top_services'] == []
        
    def test_create_cost_summary_with_data(self):
        """Test cost summary creation with cost data."""
        cost_data = [
            CostData(service_name='Vertex AI', date='2023-01-01', cost_usd=1.5),
            CostData(service_name='Cloud Storage', date='2023-01-01', cost_usd=0.5),
            CostData(service_name='Vertex AI', date='2023-01-02', cost_usd=1.0)
        ]
        total_cost = 3.0
        days = 2
        
        summary = self.cost_tracker._create_cost_summary(cost_data, days, total_cost)
        
        assert summary['success'] is True
        assert summary['period_days'] == 2
        assert summary['total_cost_usd'] == 3.0
        assert summary['threshold_usd'] == 4.0  # 2.0 * 2 days
        assert summary['alert_triggered'] is False
        assert len(summary['cost_breakdown']) == 3
        assert len(summary['top_services']) == 2
        
        # Check that services are sorted by cost
        assert summary['top_services'][0]['service'] == 'Vertex AI'
        assert summary['top_services'][0]['cost_usd'] == 2.5  # 1.5 + 1.0
        assert summary['top_services'][1]['service'] == 'Cloud Storage'
        assert summary['top_services'][1]['cost_usd'] == 0.5
        
    @patch('modules.cost_tracker.cost_tracker.smtplib.SMTP')
    def test_send_email_alert_success(self, mock_smtp):
        """Test successful email alert sending."""
        # Configure email settings
        self.cost_tracker.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_user': 'test@example.com',
            'email_password': 'password',
            'alert_recipient': 'admin@example.com'
        }
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        cost_summary = {
            'total_cost_usd': 3.0,
            'threshold_usd': 2.0,
            'period_days': 1,
            'alert_triggered': True,
            'top_services': [
                {'service': 'Vertex AI', 'cost_usd': 2.0},
                {'service': 'Cloud Storage', 'cost_usd': 1.0}
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        self.cost_tracker._send_email_alert(cost_summary)
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'password')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
        
    def test_send_email_alert_missing_config(self):
        """Test email alert with missing configuration."""
        # Clear email config
        self.cost_tracker.email_config = {
            'email_user': None,
            'email_password': None,
            'alert_recipient': None
        }
        
        cost_summary = {
            'total_cost_usd': 3.0,
            'threshold_usd': 2.0,
            'period_days': 1,
            'alert_triggered': True,
            'top_services': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Should not raise exception, just log warning
        self.cost_tracker._send_email_alert(cost_summary)
        
    @patch.object(CostTracker, '_send_email_alert')
    @patch.object(CostTracker, '_send_sms_alert')
    @patch.object(CostTracker, '_send_slack_alert')
    def test_send_alert_multiple_channels(self, mock_slack, mock_sms, mock_email):
        """Test sending alerts to multiple channels."""
        self.cost_tracker.alert_config.alert_channels = ['email', 'sms', 'slack']
        
        cost_summary = {
            'total_cost_usd': 3.0,
            'alert_triggered': True
        }
        
        self.cost_tracker._send_alert(cost_summary)
        
        mock_email.assert_called_once_with(cost_summary)
        mock_sms.assert_called_once_with(cost_summary)
        mock_slack.assert_called_once_with(cost_summary)
        
    def test_save_cost_history(self):
        """Test saving cost history."""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_cost_usd': 1.5,
            'period_days': 1
        }
        
        initial_length = len(self.cost_tracker.cost_history)
        self.cost_tracker._save_cost_history(summary)
        
        assert len(self.cost_tracker.cost_history) == initial_length + 1
        assert self.cost_tracker.cost_history[-1] == summary
        
    def test_save_cost_history_limit(self):
        """Test cost history size limit."""
        # Fill history with 101 items
        for i in range(101):
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_cost_usd': i,
                'period_days': 1
            }
            self.cost_tracker._save_cost_history(summary)
            
        # Should be limited to 100 items
        assert len(self.cost_tracker.cost_history) == 100
        
    def test_get_cost_history(self):
        """Test getting cost history."""
        # Add some history
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_cost_usd': 1.5,
            'period_days': 1
        }
        self.cost_tracker._save_cost_history(summary)
        
        history = self.cost_tracker.get_cost_history()
        assert isinstance(history, list)
        assert len(history) == 1
        assert history[0] == summary
        
    def test_set_alert_threshold(self):
        """Test setting alert threshold."""
        new_threshold = 5.0
        self.cost_tracker.set_alert_threshold(new_threshold)
        
        assert self.cost_tracker.alert_threshold == new_threshold
        assert self.cost_tracker.alert_config.threshold_usd == new_threshold
        
    def test_enable_alerts(self):
        """Test enabling alerts."""
        self.cost_tracker.alert_config.enabled = False
        self.cost_tracker.enable_alerts()
        
        assert self.cost_tracker.alert_config.enabled is True
        
    def test_disable_alerts(self):
        """Test disabling alerts."""
        self.cost_tracker.alert_config.enabled = True
        self.cost_tracker.disable_alerts()
        
        assert self.cost_tracker.alert_config.enabled is False
        
    @patch.object(CostTracker, '_query_bigquery_costs')
    @patch.object(CostTracker, '_query_billing_api_costs')
    def test_check_cost_success(self, mock_billing, mock_bigquery):
        """Test successful cost checking."""
        # Mock BigQuery returning cost data
        mock_cost_data = [
            CostData(service_name='Vertex AI', date='2023-01-01', cost_usd=1.5),
            CostData(service_name='Cloud Storage', date='2023-01-01', cost_usd=0.5)
        ]
        mock_bigquery.return_value = mock_cost_data
        mock_billing.return_value = None
        
        result = self.cost_tracker.check_cost(days=1)
        
        assert result['success'] is True
        assert result['total_cost_usd'] == 2.0
        assert result['period_days'] == 1
        assert result['alert_triggered'] is False  # 2.0 = threshold
        
    @patch.object(CostTracker, '_query_bigquery_costs')
    @patch.object(CostTracker, '_query_billing_api_costs')
    def test_check_cost_no_data(self, mock_billing, mock_bigquery):
        """Test cost checking with no data available."""
        mock_bigquery.return_value = None
        mock_billing.return_value = None
        
        result = self.cost_tracker.check_cost(days=1)
        
        assert result['success'] is True
        assert result['total_cost_usd'] == 0.0
        assert result['alert_triggered'] is False
        
    @patch.object(CostTracker, '_query_bigquery_costs')
    def test_check_cost_with_alert(self, mock_bigquery):
        """Test cost checking that triggers an alert."""
        # Mock cost data that exceeds threshold
        mock_cost_data = [
            CostData(service_name='Vertex AI', date='2023-01-01', cost_usd=3.0)
        ]
        mock_bigquery.return_value = mock_cost_data
        
        with patch.object(self.cost_tracker, '_send_alert') as mock_send_alert:
            result = self.cost_tracker.check_cost(days=1)
            
            assert result['success'] is True
            assert result['total_cost_usd'] == 3.0
            assert result['alert_triggered'] is True
            mock_send_alert.assert_called_once()
            
    @patch.object(CostTracker, '_query_bigquery_costs')
    def test_check_cost_exception(self, mock_bigquery):
        """Test cost checking with exception."""
        mock_bigquery.side_effect = Exception("BigQuery error")
        
        result = self.cost_tracker.check_cost(days=1)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'BigQuery error' in result['error']
        
    @patch.object(CostTracker, 'check_cost')
    def test_get_weekly_costs(self, mock_check_cost):
        """Test getting weekly costs."""
        mock_check_cost.return_value = {'period_days': 7, 'total_cost_usd': 10.0}
        
        result = self.cost_tracker.get_weekly_costs()
        
        mock_check_cost.assert_called_once_with(days=7)
        assert result['period_days'] == 7
        
    @patch.object(CostTracker, 'check_cost')
    def test_get_monthly_costs(self, mock_check_cost):
        """Test getting monthly costs."""
        mock_check_cost.return_value = {'period_days': 30, 'total_cost_usd': 50.0}
        
        result = self.cost_tracker.get_monthly_costs()
        
        mock_check_cost.assert_called_once_with(days=30)
        assert result['period_days'] == 30


class TestCostData:
    """Test cases for CostData dataclass."""
    
    def test_cost_data_creation(self):
        """Test CostData creation."""
        cost_data = CostData(
            service_name='Vertex AI',
            date='2023-01-01',
            cost_usd=1.5
        )
        
        assert cost_data.service_name == 'Vertex AI'
        assert cost_data.date == '2023-01-01'
        assert cost_data.cost_usd == 1.5
        assert cost_data.currency == 'USD'
        assert cost_data.usage_units is None
        assert cost_data.usage_amount is None
        
    def test_cost_data_with_usage(self):
        """Test CostData with usage information."""
        cost_data = CostData(
            service_name='Vertex AI',
            date='2023-01-01',
            cost_usd=1.5,
            currency='USD',
            usage_units='requests',
            usage_amount=1000.0
        )
        
        assert cost_data.usage_units == 'requests'
        assert cost_data.usage_amount == 1000.0


class TestCostAlert:
    """Test cases for CostAlert dataclass."""
    
    def test_cost_alert_creation(self):
        """Test CostAlert creation."""
        alert = CostAlert(
            threshold_usd=2.0,
            period_days=1,
            alert_channels=['email']
        )
        
        assert alert.threshold_usd == 2.0
        assert alert.period_days == 1
        assert alert.alert_channels == ['email']
        assert alert.enabled is True
        
    def test_cost_alert_disabled(self):
        """Test CostAlert creation with disabled state."""
        alert = CostAlert(
            threshold_usd=5.0,
            period_days=7,
            alert_channels=['email', 'slack'],
            enabled=False
        )
        
        assert alert.threshold_usd == 5.0
        assert alert.period_days == 7
        assert alert.alert_channels == ['email', 'slack']
        assert alert.enabled is False


class TestStandaloneFunctions:
    """Test cases for standalone functions."""
    
    @patch('modules.cost_tracker.cost_tracker.CostTracker')
    def test_check_cost_function(self, mock_cost_tracker_class):
        """Test standalone check_cost function."""
        mock_instance = Mock()
        mock_instance.check_cost.return_value = {'total_cost_usd': 1.5}
        mock_cost_tracker_class.return_value = mock_instance
        
        result = check_cost()
        
        mock_cost_tracker_class.assert_called_once()
        mock_instance.check_cost.assert_called_once_with()
        assert result['total_cost_usd'] == 1.5