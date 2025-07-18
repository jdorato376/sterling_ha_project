#!/usr/bin/env python3
"""
Sterling HA Agent - Automated pipeline runner for the Sterling HA project.
Handles code analysis, testing, and deployment automation.
"""

import os
import sys
import subprocess
import json
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
    """Main agent class for Sterling HA automation"""
    
    def __init__(self, repo_root=None):
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def run_command(self, command, cwd=None):
        """Execute a shell command and return result"""
        try:
            cwd = cwd or self.repo_root
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd,
                capture_output=True, 
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Command failed: {command} - {e}")
            return False, "", str(e)
    
    def lint_scripts(self):
        """Run ShellCheck on all scripts"""
        logger.info("Running ShellCheck on scripts...")
        success, stdout, stderr = self.run_command("shellcheck -e SC2181 scripts/*.sh")
        if success:
            logger.info("ShellCheck passed")
        else:
            logger.error(f"ShellCheck failed: {stderr}")
        return success
    
    def run_tests(self):
        """Run pytest on phase modules"""
        logger.info("Running pytest on phase modules...")
        # First scaffold phase stubs
        success, _, _ = self.run_command("python scripts/scaffold_phases.py")
        if not success:
            logger.error("Failed to scaffold phases")
            return False
            
        # Run tests
        success, stdout, stderr = self.run_command("python -m pytest tests/test_phase_* -q")
        if success:
            logger.info("Tests passed")
        else:
            logger.error(f"Tests failed: {stderr}")
        return success
    
    def analyze_code_diff(self):
        """Analyze git diff for changes"""
        logger.info("Analyzing code changes...")
        success, stdout, stderr = self.run_command("git diff --name-only")
        if success:
            changed_files = stdout.strip().split('\n') if stdout.strip() else []
            logger.info(f"Changed files: {changed_files}")
            return changed_files
        return []
    
    def update_agent_scorecard(self, results):
        """Update agent scorecard with results"""
        scorecard_path = self.repo_root / "agent_scorecard.json"
        
        scorecard_data = {
            "timestamp": self.timestamp,
            "lint_passed": results.get("lint", False),
            "tests_passed": results.get("tests", False),
            "changed_files": results.get("changed_files", []),
            "status": "success" if all([results.get("lint", False), results.get("tests", False)]) else "failed"
        }
        
        try:
            with open(scorecard_path, 'w') as f:
                json.dump(scorecard_data, f, indent=2)
            logger.info(f"Updated agent scorecard: {scorecard_path}")
        except Exception as e:
            logger.error(f"Failed to update scorecard: {e}")
    
    def run_full_pipeline(self):
        """Run the complete agent pipeline"""
        logger.info("Starting Sterling HA Agent pipeline...")
        
        results = {}
        
        # 1. Lint scripts
        results["lint"] = self.lint_scripts()
        
        # 2. Run tests
        results["tests"] = self.run_tests()
        
        # 3. Analyze changes
        results["changed_files"] = self.analyze_code_diff()
        
        # 4. Update scorecard
        self.update_agent_scorecard(results)
        
        # 5. Report results
        if results["lint"] and results["tests"]:
            logger.info("🎉 Agent pipeline completed successfully!")
            return True
        else:
            logger.error("❌ Agent pipeline failed!")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    else:
        repo_root = None
    
    agent = SterlingAgent(repo_root)
    success = agent.run_full_pipeline()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()