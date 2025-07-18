"""
Sterling HA Project - Cost Tracker
Phase 7: LLM Cost Tracker
Monitors daily LLM spend via BigQuery or Billing API.
Sends SMS/email alerts if > $2/day.
"""

import os
import json
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from google.cloud import bigquery
    from google.cloud import billing_v1
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    bigquery = None
    billing_v1 = None

logger = logging.getLogger(__name__)

@dataclass
class CostData:
    """Represents cost data for a specific service or time period."""
    service_name: str
    date: str
    cost_usd: float
    currency: str = "USD"
    usage_units: Optional[str] = None
    usage_amount: Optional[float] = None
    
@dataclass
class CostAlert:
    """Represents a cost alert configuration."""
    threshold_usd: float
    period_days: int
    alert_channels: List[str]  # email, sms, slack, etc.
    enabled: bool = True

class CostTracker:
    """Main cost tracking class for monitoring LLM and cloud spending."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.project_id = self.config.get('project_id') or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.billing_account_id = self.config.get('billing_account_id') or os.getenv('BILLING_ACCOUNT_ID')
        self.alert_threshold = self.config.get('alert_threshold', 2.0)  # $2/day default
        self.cost_history = []
        
        # Alert configuration
        self.alert_config = CostAlert(
            threshold_usd=self.alert_threshold,
            period_days=1,
            alert_channels=self.config.get('alert_channels', ['email']),
            enabled=self.config.get('alerts_enabled', True)
        )
        
        # Email configuration
        self.email_config = {
            'smtp_server': self.config.get('smtp_server', 'smtp.gmail.com'),
            'smtp_port': self.config.get('smtp_port', 587),
            'email_user': self.config.get('email_user') or os.getenv('EMAIL_USER'),
            'email_password': self.config.get('email_password') or os.getenv('EMAIL_PASSWORD'),
            'alert_recipient': self.config.get('alert_recipient') or os.getenv('EMAIL_ALERT_RECIPIENT')
        }
        
        # Initialize clients
        self.bigquery_client = None
        self.billing_client = None
        
        if GOOGLE_CLOUD_AVAILABLE and self.project_id:
            try:
                self.bigquery_client = bigquery.Client(project=self.project_id)
                self.billing_client = billing_v1.CloudBillingClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud clients: {e}")
                
    def check_cost(self, days: int = 1) -> Dict[str, Any]:
        """Check cost for the specified number of days."""
        logger.info(f"Checking costs for the last {days} days")
        
        try:
            # Try BigQuery first, then Billing API
            cost_data = self._query_bigquery_costs(days) or self._query_billing_api_costs(days)
            
            if not cost_data:
                logger.warning("No cost data available from any source")
                return self._create_cost_summary([], days)
                
            # Calculate total cost
            total_cost = sum(cost.cost_usd for cost in cost_data)
            
            # Check if alert threshold is exceeded
            should_alert = self._should_alert(total_cost, days)
            
            # Create summary
            summary = self._create_cost_summary(cost_data, days, total_cost)
            
            # Send alert if necessary
            if should_alert and self.alert_config.enabled:
                self._send_alert(summary)
                
            # Save to history
            self._save_cost_history(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error checking costs: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def _query_bigquery_costs(self, days: int) -> Optional[List[CostData]]:
        """Query costs from BigQuery billing export."""
        if not self.bigquery_client or not self.project_id:
            return None
            
        try:
            # Query for the last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = f"""
            SELECT 
                service.description as service_name,
                DATE(usage_start_time) as usage_date,
                SUM(cost) as total_cost,
                currency
            FROM `{self.project_id}.cloud_billing_export.gcp_billing_export_*`
            WHERE DATE(usage_start_time) BETWEEN '{start_date.strftime('%Y-%m-%d')}' 
                AND '{end_date.strftime('%Y-%m-%d')}'
                AND cost > 0
            GROUP BY service_name, usage_date, currency
            ORDER BY usage_date DESC, total_cost DESC
            """
            
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            cost_data = []
            for row in results:
                cost_data.append(CostData(
                    service_name=row.service_name,
                    date=row.usage_date.strftime('%Y-%m-%d'),
                    cost_usd=float(row.total_cost),
                    currency=row.currency
                ))
                
            logger.info(f"Retrieved {len(cost_data)} cost records from BigQuery")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error querying BigQuery: {e}")
            return None
            
    def _query_billing_api_costs(self, days: int) -> Optional[List[CostData]]:
        """Query costs from Cloud Billing API."""
        if not self.billing_client or not self.billing_account_id:
            return None
            
        try:
            # This is a simplified example - the actual Billing API 
            # requires more complex setup for cost queries
            logger.info("Billing API cost querying not fully implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error querying Billing API: {e}")
            return None
            
    def _should_alert(self, total_cost: float, days: int) -> bool:
        """Determine if an alert should be sent based on cost thresholds."""
        daily_threshold = self.alert_config.threshold_usd
        period_threshold = daily_threshold * days
        
        return total_cost > period_threshold
        
    def _create_cost_summary(self, cost_data: List[CostData], days: int, total_cost: float = 0.0) -> Dict[str, Any]:
        """Create a cost summary report."""
        summary = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'total_cost_usd': total_cost,
            'threshold_usd': self.alert_config.threshold_usd * days,
            'alert_triggered': total_cost > (self.alert_config.threshold_usd * days),
            'cost_breakdown': [],
            'top_services': []
        }
        
        # Group costs by service
        service_costs = {}
        for cost in cost_data:
            if cost.service_name not in service_costs:
                service_costs[cost.service_name] = 0.0
            service_costs[cost.service_name] += cost.cost_usd
            
        # Sort services by cost
        sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        
        # Add top services
        summary['top_services'] = [
            {'service': service, 'cost_usd': cost}
            for service, cost in sorted_services[:5]
        ]
        
        # Add detailed breakdown
        summary['cost_breakdown'] = [asdict(cost) for cost in cost_data]
        
        return summary
        
    def _send_alert(self, cost_summary: Dict[str, Any]) -> None:
        """Send cost alert via configured channels."""
        logger.info("Sending cost alert")
        
        for channel in self.alert_config.alert_channels:
            try:
                if channel == 'email':
                    self._send_email_alert(cost_summary)
                elif channel == 'sms':
                    self._send_sms_alert(cost_summary)
                elif channel == 'slack':
                    self._send_slack_alert(cost_summary)
                else:
                    logger.warning(f"Unknown alert channel: {channel}")
                    
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
                
    def _send_email_alert(self, cost_summary: Dict[str, Any]) -> None:
        """Send email alert."""
        if not all([
            self.email_config['email_user'],
            self.email_config['email_password'],
            self.email_config['alert_recipient']
        ]):
            logger.warning("Email configuration incomplete, skipping email alert")
            return
            
        subject = f"Sterling HA Cost Alert - ${cost_summary['total_cost_usd']:.2f}"
        
        body = f"""
        Cost Alert: Daily spending threshold exceeded
        
        Summary:
        - Period: {cost_summary['period_days']} days
        - Total Cost: ${cost_summary['total_cost_usd']:.2f}
        - Threshold: ${cost_summary['threshold_usd']:.2f}
        - Alert Triggered: {cost_summary['alert_triggered']}
        
        Top Services:
        """
        
        for service in cost_summary['top_services']:
            body += f"- {service['service']}: ${service['cost_usd']:.2f}\n"
            
        body += f"""
        
        Timestamp: {cost_summary['timestamp']}
        
        Please review your cloud spending and take action if necessary.
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email_user']
            msg['To'] = self.email_config['alert_recipient']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email_user'], self.email_config['email_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            
    def _send_sms_alert(self, cost_summary: Dict[str, Any]) -> None:
        """Send SMS alert (placeholder for Twilio integration)."""
        logger.info("SMS alerts not yet implemented")
        
    def _send_slack_alert(self, cost_summary: Dict[str, Any]) -> None:
        """Send Slack alert (placeholder for Slack webhook integration)."""
        logger.info("Slack alerts not yet implemented")
        
    def _save_cost_history(self, summary: Dict[str, Any]) -> None:
        """Save cost summary to history."""
        self.cost_history.append(summary)
        
        # Keep only last 100 records
        if len(self.cost_history) > 100:
            self.cost_history = self.cost_history[-100:]
            
    def get_cost_history(self) -> List[Dict[str, Any]]:
        """Get the cost history."""
        return self.cost_history
        
    def get_monthly_costs(self) -> Dict[str, Any]:
        """Get monthly cost summary."""
        return self.check_cost(days=30)
        
    def get_weekly_costs(self) -> Dict[str, Any]:
        """Get weekly cost summary."""
        return self.check_cost(days=7)
        
    def set_alert_threshold(self, threshold_usd: float) -> None:
        """Set the alert threshold."""
        self.alert_config.threshold_usd = threshold_usd
        self.alert_threshold = threshold_usd
        logger.info(f"Alert threshold set to ${threshold_usd:.2f}")
        
    def enable_alerts(self) -> None:
        """Enable cost alerts."""
        self.alert_config.enabled = True
        logger.info("Cost alerts enabled")
        
    def disable_alerts(self) -> None:
        """Disable cost alerts."""
        self.alert_config.enabled = False
        logger.info("Cost alerts disabled")


# Standalone function for backwards compatibility
def check_cost():
    """Check cost using default configuration."""
    tracker = CostTracker()
    return tracker.check_cost()
