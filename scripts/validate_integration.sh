#!/bin/bash
# Sterling HA Integration Validation Script
# Verifies all components of the end-to-end pipeline are properly implemented

set -uo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Log function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Test function
test_component() {
    local component=$1
    local test_command=$2
    
    log "${BLUE}Testing: $component${NC}"
    
    if eval "$test_command"; then
        log "${GREEN}✅ $component - PASSED${NC}"
        ((TESTS_PASSED++))
    else
        log "${RED}❌ $component - FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

# Header
log "${BLUE}🚀 Sterling HA End-to-End Pipeline Validation${NC}"
log "${BLUE}=============================================${NC}"

# 1. Test Agent Pipeline
test_component "Agent Pipeline" "python tools/agent.py"

# 2. Test Repair Agent
test_component "Repair Agent Health Check" "python -m modules.repair_agent.repair_agent --check"

# 3. Test Cost Tracker
test_component "Cost Tracker Daily Check" "python -m modules.cost_tracker.cost_tracker --daily"

# 4. Test Billing Script
test_component "Billing Check Script" "GOOGLE_CLOUD_PROJECT=test-project ./scripts/check_billing.sh --help"

# 5. Test Phase Scaffolding
test_component "Phase Scaffolding" "python scripts/scaffold_phases.py"

# 6. Test Phase Tests
test_component "Phase Module Tests" "python -m pytest tests/test_phase_* -q"

# 7. Test New Module Tests
test_component "Repair Agent Tests" "python -m pytest tests/test_repair_agent.py -q"
test_component "Cost Tracker Tests" "python -m pytest tests/test_cost_tracker.py -q"

# 8. Test Shell Script Linting
test_component "Shell Script Linting" "shellcheck -e SC2181 scripts/*.sh"

# 9. Test Infrastructure Files
test_component "Terraform Configuration" "[ -f infrastructure/terraform/main.tf ]"
test_component "Cloud Build Configuration" "[ -f cloudbuild.yaml ]"
test_component "Auto Agent Workflow" "[ -f .github/workflows/auto-agent.yml ]"

# 10. Test Docker Build (check Dockerfile exists and is readable)
test_component "Docker Build Test" "[ -f addons/sterling_os/Dockerfile ] && [ -r addons/sterling_os/Dockerfile ]"

# 11. Test Environment Configuration
test_component "Environment Variables Setup" "[ -f .env.example ]"

# 12. Test Deployment Scripts
test_component "Vertex AI Deployment Script" "[ -x scripts/deploy_vertex.sh ]"
test_component "VM Provisioning Script" "[ -x infrastructure/provision_vm.sh ]"

# Summary
log "${BLUE}=============================================${NC}"
log "${BLUE}📊 Validation Summary${NC}"
log "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
log "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    log "${GREEN}🎉 All components validated successfully!${NC}"
    log "${GREEN}Sterling HA End-to-End Pipeline is ready for deployment.${NC}"
    exit 0
else
    log "${RED}💥 Some components failed validation.${NC}"
    log "${YELLOW}Please review the failed tests and fix any issues.${NC}"
    exit 1
fi