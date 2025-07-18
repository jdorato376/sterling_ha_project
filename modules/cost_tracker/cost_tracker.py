"""
Sterling HA Cost Tracker
Monitors GCP and AI service costs, provides billing alerts and cost optimization.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from google.cloud import bigquery
    from google.cloud import monitoring_v3
    from google.cloud.exceptions import NotFound
    HAS_GOOGLE_CLOUD = True
except ImportError:
    HAS_GOOGLE_CLOUD = False

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Cost tracking and billing management for Sterling HA project.
    Monitors GCP costs, AI service usage, and provides alerts.
    """
    
    def __init__(self, project_id: Optional[str] = None, config_path: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.config_path = config_path or "modules/cost_tracker/cost_config.json"
        self.config = self._load_config()
        
        # Initialize clients if Google Cloud libraries are available
        self.bigquery_client = None
        self.monitoring_client = None
        
        if HAS_GOOGLE_CLOUD and self.project_id:
            try:
                self.bigquery_client = bigquery.Client(project=self.project_id)
                self.monitoring_client = monitoring_v3.MetricServiceClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud clients: {e}")
        
        self.cost_history: List[Dict[str, Any]] = []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load cost tracker configuration"""
        default_config = {
            "daily_cost_threshold": 2.0,
            "monthly_cost_threshold": 50.0,
            "cost_check_interval": 3600,  # 1 hour
            "alert_channels": {
                "email": os.getenv("ALERT_EMAIL", ""),
                "slack_webhook": os.getenv("SLACK_WEBHOOK", ""),
                "sms_number": os.getenv("SMS_NUMBER", "")
            },
            "tracked_services": [
                "aiplatform.googleapis.com",
                "compute.googleapis.com",
                "cloudbuild.googleapis.com",
                "artifactregistry.googleapis.com",
                "bigquery.googleapis.com",
                "monitoring.googleapis.com"
            ],
            "billing_export_table": "sterling_ha_analytics.billing_export",
            "cost_optimization": {
                "auto_shutdown_idle_vms": True,
                "idle_vm_threshold_hours": 2,
                "auto_cleanup_old_builds": True,
                "build_retention_days": 30
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
    
    def check_daily_costs(self) -> Dict[str, Any]:
        """Check daily costs across all tracked services"""
        cost_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_cost": 0.0,
            "service_costs": {},
            "threshold_exceeded": False,
            "alert_sent": False,
            "error": None
        }
        
        try:
            if self.bigquery_client:
                cost_data = self._query_bigquery_costs(cost_data)
            else:
                # Fallback to mock data for testing
                cost_data = self._get_mock_costs(cost_data)
                
            # Check if threshold exceeded
            threshold = self.config["daily_cost_threshold"]
            if cost_data["total_cost"] > threshold:
                cost_data["threshold_exceeded"] = True
                logger.warning(f"Daily cost threshold exceeded: ${cost_data['total_cost']:.2f} > ${threshold:.2f}")
                
                # Send alert
                if self._send_cost_alert(cost_data, "daily"):
                    cost_data["alert_sent"] = True
                    
        except Exception as e:
            cost_data["error"] = str(e)
            logger.error(f"Error checking daily costs: {e}")
        
        self.cost_history.append(cost_data)
        return cost_data
    
    def check_monthly_costs(self) -> Dict[str, Any]:
        """Check monthly costs across all tracked services"""
        cost_data = {
            "month": datetime.now().strftime("%Y-%m"),
            "total_cost": 0.0,
            "service_costs": {},
            "threshold_exceeded": False,
            "alert_sent": False,
            "error": None
        }
        
        try:
            if self.bigquery_client:
                cost_data = self._query_bigquery_monthly_costs(cost_data)
            else:
                # Fallback to mock data for testing
                cost_data = self._get_mock_monthly_costs(cost_data)
                
            # Check if threshold exceeded
            threshold = self.config["monthly_cost_threshold"]
            if cost_data["total_cost"] > threshold:
                cost_data["threshold_exceeded"] = True
                logger.warning(f"Monthly cost threshold exceeded: ${cost_data['total_cost']:.2f} > ${threshold:.2f}")
                
                # Send alert
                if self._send_cost_alert(cost_data, "monthly"):
                    cost_data["alert_sent"] = True
                    
        except Exception as e:
            cost_data["error"] = str(e)
            logger.error(f"Error checking monthly costs: {e}")
        
        return cost_data
    
    def _query_bigquery_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query BigQuery for daily cost data"""
        if not self.bigquery_client:
            raise Exception("BigQuery client not initialized")
        
        table_name = self.config["billing_export_table"]
        query = f"""
        SELECT 
            service.description as service_name,
            SUM(cost) as total_cost,
            currency
        FROM `{self.project_id}.{table_name}`
        WHERE DATE(usage_start_time) = CURRENT_DATE()
        GROUP BY service.description, currency
        ORDER BY total_cost DESC
        """
        
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            total_cost = 0.0
            service_costs = {}
            
            for row in results:
                service_name = row.service_name
                service_cost = float(row.total_cost)
                service_costs[service_name] = service_cost
                total_cost += service_cost
            
            cost_data["total_cost"] = total_cost
            cost_data["service_costs"] = service_costs
            
        except NotFound:
            logger.warning(f"Billing export table not found: {table_name}")
            cost_data["error"] = "Billing export table not found"
        except Exception as e:
            logger.error(f"Error querying BigQuery: {e}")
            cost_data["error"] = str(e)
        
        return cost_data
    
    def _query_bigquery_monthly_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query BigQuery for monthly cost data"""
        if not self.bigquery_client:
            raise Exception("BigQuery client not initialized")
        
        table_name = self.config["billing_export_table"]
        query = f"""
        SELECT 
            service.description as service_name,
            SUM(cost) as total_cost,
            currency
        FROM `{self.project_id}.{table_name}`
        WHERE DATE(usage_start_time) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
        GROUP BY service.description, currency
        ORDER BY total_cost DESC
        """
        
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            total_cost = 0.0
            service_costs = {}
            
            for row in results:
                service_name = row.service_name
                service_cost = float(row.total_cost)
                service_costs[service_name] = service_cost
                total_cost += service_cost
            
            cost_data["total_cost"] = total_cost
            cost_data["service_costs"] = service_costs
            
        except Exception as e:
            logger.error(f"Error querying BigQuery monthly costs: {e}")
            cost_data["error"] = str(e)
        
        return cost_data
    
    def _get_mock_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock cost data for testing"""
        import random
        
        # Generate realistic mock costs
        service_costs = {}
        total_cost = 0.0
        
        for service in self.config["tracked_services"]:
            service_name = service.replace(".googleapis.com", "")
            cost = random.uniform(0.1, 0.5)  # Random cost between $0.10 and $0.50
            service_costs[service_name] = cost
            total_cost += cost
        
        cost_data["total_cost"] = round(total_cost, 2)
        cost_data["service_costs"] = service_costs
        
        return cost_data
    
    def _get_mock_monthly_costs(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get mock monthly cost data for testing"""
        import random
        
        # Generate realistic mock monthly costs
        service_costs = {}
        total_cost = 0.0
        
        for service in self.config["tracked_services"]:
            service_name = service.replace(".googleapis.com", "")
            cost = random.uniform(2.0, 15.0)  # Random cost between $2.00 and $15.00
            service_costs[service_name] = cost
            total_cost += cost
        
        cost_data["total_cost"] = round(total_cost, 2)
        cost_data["service_costs"] = service_costs
        
        return cost_data
    
    def _send_cost_alert(self, cost_data: Dict[str, Any], period: str) -> bool:
        """Send cost alert via configured channels"""
        alert_sent = False
        
        message = self._format_alert_message(cost_data, period)
        
        # Email alert
        if self.config["alert_channels"]["email"]:
            if self._send_email_alert(message):
                alert_sent = True
        
        # Slack alert
        if self.config["alert_channels"]["slack_webhook"]:
            if self._send_slack_alert(message):
                alert_sent = True
        
        # SMS alert
        if self.config["alert_channels"]["sms_number"]:
            if self._send_sms_alert(message):
                alert_sent = True
        
        return alert_sent
    
    def _format_alert_message(self, cost_data: Dict[str, Any], period: str) -> str:
        """Format alert message"""
        threshold = self.config[f"{period}_cost_threshold"]
        
        message = f"""
🚨 Sterling HA Cost Alert - {period.title()} Threshold Exceeded

Current {period} cost: ${cost_data['total_cost']:.2f}
Threshold: ${threshold:.2f}
Date: {cost_data.get('date', cost_data.get('month', 'N/A'))}

Top Services:
"""
        
        # Add top 3 services by cost
        sorted_services = sorted(
            cost_data["service_costs"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        for service, cost in sorted_services:
            message += f"• {service}: ${cost:.2f}\n"
        
        message += "\nPlease review and optimize resource usage."
        
        return message
    
    def _send_email_alert(self, message: str) -> bool:
        """Send email alert (placeholder implementation)"""
        # In a real implementation, this would use sendmail, SMTP, or a service like SendGrid
        logger.info(f"Email alert (placeholder): {message}")
        return True
    
    def _send_slack_alert(self, message: str) -> bool:
        """Send Slack alert (placeholder implementation)"""
        # In a real implementation, this would use the Slack webhook
        logger.info(f"Slack alert (placeholder): {message}")
        return True
    
    def _send_sms_alert(self, message: str) -> bool:
        """Send SMS alert (placeholder implementation)"""
        # In a real implementation, this would use Twilio or similar
        logger.info(f"SMS alert (placeholder): {message}")
        return True
    
    def get_cost_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        # Check for idle VMs
        if self.config["cost_optimization"]["auto_shutdown_idle_vms"]:
            idle_vms = self._find_idle_vms()
            if idle_vms:
                recommendations.append({
                    "type": "idle_vm_shutdown",
                    "priority": "high",
                    "description": f"Found {len(idle_vms)} idle VMs that can be shut down",
                    "potential_savings": self._calculate_vm_savings(idle_vms),
                    "action": "shutdown_idle_vms",
                    "details": idle_vms
                })
        
        # Check for old builds
        if self.config["cost_optimization"]["auto_cleanup_old_builds"]:
            old_builds = self._find_old_builds()
            if old_builds:
                recommendations.append({
                    "type": "cleanup_old_builds",
                    "priority": "medium",
                    "description": f"Found {len(old_builds)} old builds that can be cleaned up",
                    "potential_savings": self._calculate_build_savings(old_builds),
                    "action": "cleanup_old_builds",
                    "details": old_builds
                })
        
        return recommendations
    
    def _find_idle_vms(self) -> List[Dict[str, Any]]:
        """Find idle VMs (placeholder implementation)"""
        # In a real implementation, this would check VM metrics
        return []
    
    def _find_old_builds(self) -> List[Dict[str, Any]]:
        """Find old builds (placeholder implementation)"""
        # In a real implementation, this would check Cloud Build history
        return []
    
    def _calculate_vm_savings(self, idle_vms: List[Dict[str, Any]]) -> float:
        """Calculate potential VM savings"""
        # Placeholder calculation
        return len(idle_vms) * 0.50  # $0.50 per VM per day
    
    def _calculate_build_savings(self, old_builds: List[Dict[str, Any]]) -> float:
        """Calculate potential build cleanup savings"""
        # Placeholder calculation
        return len(old_builds) * 0.10  # $0.10 per build
    
    def optimize_costs(self) -> Dict[str, Any]:
        """Perform automated cost optimization"""
        optimization_result = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "total_savings": 0.0,
            "errors": []
        }
        
        recommendations = self.get_cost_recommendations()
        
        for recommendation in recommendations:
            try:
                if recommendation["action"] == "shutdown_idle_vms":
                    result = self._shutdown_idle_vms(recommendation["details"])
                    optimization_result["actions_taken"].append(result)
                    optimization_result["total_savings"] += result.get("savings", 0.0)
                    
                elif recommendation["action"] == "cleanup_old_builds":
                    result = self._cleanup_old_builds(recommendation["details"])
                    optimization_result["actions_taken"].append(result)
                    optimization_result["total_savings"] += result.get("savings", 0.0)
                    
            except Exception as e:
                optimization_result["errors"].append({
                    "recommendation": recommendation["type"],
                    "error": str(e)
                })
                logger.error(f"Error optimizing costs: {e}")
        
        return optimization_result
    
    def _shutdown_idle_vms(self, idle_vms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Shutdown idle VMs (placeholder implementation)"""
        return {
            "action": "shutdown_idle_vms",
            "count": len(idle_vms),
            "savings": len(idle_vms) * 0.50,
            "success": True
        }
    
    def _cleanup_old_builds(self, old_builds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cleanup old builds (placeholder implementation)"""
        return {
            "action": "cleanup_old_builds",
            "count": len(old_builds),
            "savings": len(old_builds) * 0.10,
            "success": True
        }
    
    def get_cost_history(self) -> List[Dict[str, Any]]:
        """Get historical cost data"""
        return self.cost_history
    
    def export_cost_report(self, output_path: str) -> str:
        """Export cost report to file"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "project_id": self.project_id,
            "daily_costs": self.check_daily_costs(),
            "monthly_costs": self.check_monthly_costs(),
            "recommendations": self.get_cost_recommendations(),
            "cost_history": self.cost_history
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_path


def check_cost():
    """Main cost checking function for backwards compatibility"""
    tracker = CostTracker()
    daily_costs = tracker.check_daily_costs()
    
    if daily_costs["threshold_exceeded"]:
        logger.warning(f"Daily cost threshold exceeded: ${daily_costs['total_cost']:.2f}")
        return False
    
    return True


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sterling HA Cost Tracker")
    parser.add_argument("--daily", action="store_true", help="Check daily costs")
    parser.add_argument("--monthly", action="store_true", help="Check monthly costs")
    parser.add_argument("--optimize", action="store_true", help="Run cost optimization")
    parser.add_argument("--report", help="Export cost report to file")
    parser.add_argument("--project", help="GCP Project ID")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tracker = CostTracker(args.project)
    
    if args.daily:
        daily_costs = tracker.check_daily_costs()
        print(json.dumps(daily_costs, indent=2))
        
    elif args.monthly:
        monthly_costs = tracker.check_monthly_costs()
        print(json.dumps(monthly_costs, indent=2))
        
    elif args.optimize:
        optimization_result = tracker.optimize_costs()
        print(json.dumps(optimization_result, indent=2))
        
    elif args.report:
        report_path = tracker.export_cost_report(args.report)
        print(f"Cost report exported to: {report_path}")
        
    else:
        print("Use --daily, --monthly, --optimize, or --report")


if __name__ == "__main__":
    main()
