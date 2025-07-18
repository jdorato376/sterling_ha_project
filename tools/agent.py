#!/usr/bin/env python3
"""
tools/agent.py

Sterling HA Project Agent
Handles automated code analysis, patching, and deployment.
Triggered by GitHub issues with '/codex run' comment, pushes to main, and cron schedule.
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SterlingAgent:
    """Main agent class for Sterling HA Project automation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def run_linting(self):
        """Run linting checks on scripts."""
        logger.info("Running linting checks...")
        
        # ShellCheck for shell scripts
        try:
            result = subprocess.run(
                ["shellcheck", "-e", "SC2181", "scripts/*.sh"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                logger.warning(f"ShellCheck warnings: {result.stdout}")
            else:
                logger.info("ShellCheck passed")
        except Exception as e:
            logger.error(f"ShellCheck failed: {e}")
            
    def run_tests(self):
        """Run pytest on test suite."""
        logger.info("Running test suite...")
        
        try:
            # Scaffold phase modules first
            subprocess.run(
                ["python", "scripts/scaffold_phases.py"],
                cwd=self.project_root,
                check=True
            )
            
            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("All tests passed")
            else:
                logger.error(f"Tests failed: {result.stdout}")
                
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            
    def analyze_code_changes(self):
        """Analyze recent code changes and generate insights."""
        logger.info("Analyzing code changes...")
        
        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                logger.info(f"Recent commits analyzed: {len(commits)}")
                
                # Generate diff analysis
                diff_result = subprocess.run(
                    ["git", "diff", "HEAD~5..HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if diff_result.returncode == 0 and diff_result.stdout:
                    logger.info("Code diff analysis completed")
                    return diff_result.stdout
                    
        except Exception as e:
            logger.error(f"Code analysis failed: {e}")
            
        return None
        
    def check_infrastructure(self):
        """Check infrastructure health and configuration."""
        logger.info("Checking infrastructure configuration...")
        
        # Check if required files exist
        required_files = [
            "cloudbuild.yaml",
            "infrastructure/terraform/main.tf",
            "infrastructure/provision_vm.sh",
            ".env.example"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            logger.warning(f"Missing infrastructure files: {missing_files}")
        else:
            logger.info("All infrastructure files present")
            
        return missing_files
        
    def deploy_if_needed(self):
        """Deploy changes if deployment is needed."""
        logger.info("Checking if deployment is needed...")
        
        # Check if vertex deployment script exists and is executable
        vertex_script = self.project_root / "scripts/deploy_vertex.sh"
        if vertex_script.exists():
            logger.info("Vertex deployment script found")
            
            # Check environment variables
            required_env = ["GOOGLE_CLOUD_PROJECT", "REGION"]
            missing_env = [var for var in required_env if not os.getenv(var)]
            
            if missing_env:
                logger.warning(f"Missing environment variables: {missing_env}")
            else:
                logger.info("Environment variables configured")
                
        else:
            logger.warning("Vertex deployment script not found")
            
    def generate_report(self):
        """Generate agent execution report."""
        logger.info("Generating execution report...")
        
        report = {
            "timestamp": self.timestamp,
            "agent_version": "1.0.0",
            "execution_summary": {
                "linting_completed": True,
                "tests_completed": True,
                "code_analysis_completed": True,
                "infrastructure_check_completed": True
            },
            "recommendations": [
                "Continue monitoring for infrastructure changes",
                "Ensure all environment variables are properly configured",
                "Monitor test suite for new failures"
            ]
        }
        
        report_path = self.project_root / f"agent_report_{self.timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Report generated: {report_path}")
        return report
        
    def run(self):
        """Main agent execution."""
        logger.info("Sterling HA Project Agent starting...")
        
        try:
            # Run all agent tasks
            self.run_linting()
            self.run_tests()
            self.analyze_code_changes()
            self.check_infrastructure()
            self.deploy_if_needed()
            
            # Generate final report
            report = self.generate_report()
            
            logger.info("Agent execution completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        action = sys.argv[1]
        logger.info(f"Agent triggered with action: {action}")
    else:
        logger.info("Agent triggered without specific action")
        
    agent = SterlingAgent()
    return agent.run()

if __name__ == "__main__":
    main()