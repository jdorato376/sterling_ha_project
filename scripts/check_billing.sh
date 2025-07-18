#!/bin/bash
# Sterling HA BigQuery Billing Check Script
# Checks current billing costs and alerts if thresholds are exceeded

set -euo pipefail

# Load environment variables
if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    source .env
fi

# Configuration with defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
DATASET_NAME="${BIGQUERY_DATASET:-sterling_ha_analytics}"
TABLE_NAME="${BILLING_EXPORT_TABLE:-billing_export}"
DAILY_THRESHOLD="${DAILY_COST_THRESHOLD:-2.00}"
MONTHLY_THRESHOLD="${MONTHLY_COST_THRESHOLD:-50.00}"
ALERT_EMAIL="${ALERT_EMAIL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if required tools are installed
check_prerequisites() {
    if ! command -v bq &> /dev/null; then
        log "${RED}ERROR: Google Cloud SDK 'bq' command not found${NC}"
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        log "${RED}ERROR: Google Cloud SDK 'gcloud' command not found${NC}"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log "${RED}ERROR: Not authenticated with Google Cloud${NC}"
        log "Run: gcloud auth login"
        exit 1
    fi
}

# Check if BigQuery dataset and table exist
check_bigquery_setup() {
    log "Checking BigQuery setup..."
    
    # Check if dataset exists
    if ! bq show --project_id="$PROJECT_ID" "$DATASET_NAME" &>/dev/null; then
        log "${YELLOW}WARNING: BigQuery dataset '$DATASET_NAME' not found${NC}"
        log "Creating dataset..."
        
        if bq mk --project_id="$PROJECT_ID" --location=US "$DATASET_NAME"; then
            log "${GREEN}✅ Created BigQuery dataset: $DATASET_NAME${NC}"
        else
            log "${RED}ERROR: Failed to create BigQuery dataset${NC}"
            exit 1
        fi
    fi
    
    # Check if billing export table exists
    if ! bq show --project_id="$PROJECT_ID" "${DATASET_NAME}.${TABLE_NAME}" &>/dev/null; then
        log "${YELLOW}WARNING: Billing export table '${DATASET_NAME}.${TABLE_NAME}' not found${NC}"
        log "This table is automatically created when billing export is configured."
        log "To set up billing export, visit: https://console.cloud.google.com/billing/export"
        
        # Create a mock table for testing
        log "Creating mock billing table for testing..."
        bq mk --project_id="$PROJECT_ID" --table "${DATASET_NAME}.${TABLE_NAME}" \
            "service:RECORD,usage_start_time:TIMESTAMP,usage_end_time:TIMESTAMP,cost:FLOAT,currency:STRING" || true
    fi
}

# Query daily costs
check_daily_costs() {
    log "Checking daily costs..."
    
    local query="
    SELECT 
        COALESCE(SUM(cost), 0) as total_cost,
        COUNT(*) as record_count,
        STRING_AGG(DISTINCT currency) as currencies
    FROM \`${PROJECT_ID}.${DATASET_NAME}.${TABLE_NAME}\`
    WHERE DATE(usage_start_time) = CURRENT_DATE()
    "
    
    local result
    result=$(bq query --project_id="$PROJECT_ID" --use_legacy_sql=false --format=csv --max_rows=1 "$query" 2>/dev/null | tail -1)
    
    if [ -z "$result" ] || [ "$result" = "total_cost,record_count,currencies" ]; then
        log "${YELLOW}WARNING: No billing data found for today${NC}"
        echo "0.00,0,"
        return 0
    fi
    
    echo "$result"
}

# Query monthly costs
check_monthly_costs() {
    log "Checking monthly costs..."
    
    local query="
    SELECT 
        COALESCE(SUM(cost), 0) as total_cost,
        COUNT(*) as record_count,
        STRING_AGG(DISTINCT currency) as currencies
    FROM \`${PROJECT_ID}.${DATASET_NAME}.${TABLE_NAME}\`
    WHERE DATE(usage_start_time) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
    "
    
    local result
    result=$(bq query --project_id="$PROJECT_ID" --use_legacy_sql=false --format=csv --max_rows=1 "$query" 2>/dev/null | tail -1)
    
    if [ -z "$result" ] || [ "$result" = "total_cost,record_count,currencies" ]; then
        log "${YELLOW}WARNING: No billing data found for this month${NC}"
        echo "0.00,0,"
        return 0
    fi
    
    echo "$result"
}

# Query service breakdown
get_service_breakdown() {
    local period=$1  # "daily" or "monthly"
    
    local date_filter
    if [ "$period" = "daily" ]; then
        date_filter="DATE(usage_start_time) = CURRENT_DATE()"
    else
        date_filter="DATE(usage_start_time) >= DATE_TRUNC(CURRENT_DATE(), MONTH)"
    fi
    
    local query="
    SELECT 
        service.description as service_name,
        SUM(cost) as service_cost
    FROM \`${PROJECT_ID}.${DATASET_NAME}.${TABLE_NAME}\`
    WHERE ${date_filter}
    GROUP BY service.description
    HAVING service_cost > 0
    ORDER BY service_cost DESC
    LIMIT 10
    "
    
    bq query --project_id="$PROJECT_ID" --use_legacy_sql=false --format=table "$query" 2>/dev/null || true
}

# Send alert email (placeholder)
send_alert() {
    local message=$1
    local subject="🚨 Sterling HA Billing Alert"
    
    if [ -n "$ALERT_EMAIL" ]; then
        # In a real implementation, use sendmail, mail command, or API
        log "📧 Sending alert email to $ALERT_EMAIL"
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL" 2>/dev/null || {
            log "${YELLOW}WARNING: Failed to send email alert (mail command not available)${NC}"
            log "Email content would be:"
            echo "$message"
        }
    else
        log "${YELLOW}WARNING: No alert email configured${NC}"
        log "Alert message:"
        echo "$message"
    fi
}

# Format currency
format_currency() {
    local amount=$1
    printf "%.2f" "$amount"
}

# Main function
main() {
    local check_type="${1:-both}"
    
    log "🚀 Starting Sterling HA billing check..."
    log "Project: $PROJECT_ID"
    log "Dataset: $DATASET_NAME"
    log "Table: $TABLE_NAME"
    log "Daily threshold: \$${DAILY_THRESHOLD}"
    log "Monthly threshold: \$${MONTHLY_THRESHOLD}"
    
    # Check prerequisites
    check_prerequisites
    
    # Check BigQuery setup
    check_bigquery_setup
    
    local daily_exceeded=false
    local monthly_exceeded=false
    local alert_messages=""
    
    # Check daily costs
    if [ "$check_type" = "daily" ] || [ "$check_type" = "both" ]; then
        local daily_result
        daily_result=$(check_daily_costs)
        
        local daily_cost
        daily_cost=$(echo "$daily_result" | cut -d',' -f1)
        
        local daily_records
        daily_records=$(echo "$daily_result" | cut -d',' -f2)
        
        log "📊 Daily cost: \$$(format_currency "$daily_cost") (${daily_records} records)"
        
        if (( $(echo "$daily_cost > $DAILY_THRESHOLD" | bc -l) )); then
            daily_exceeded=true
            log "${RED}⚠️  DAILY THRESHOLD EXCEEDED: \$$(format_currency "$daily_cost") > \$${DAILY_THRESHOLD}${NC}"
            
            alert_messages+="🚨 Daily Cost Alert

Current daily cost: \$$(format_currency "$daily_cost")
Threshold: \$${DAILY_THRESHOLD}
Records: ${daily_records}

Top Services Today:
$(get_service_breakdown "daily")

"
        else
            log "${GREEN}✅ Daily cost within threshold${NC}"
        fi
    fi
    
    # Check monthly costs
    if [ "$check_type" = "monthly" ] || [ "$check_type" = "both" ]; then
        local monthly_result
        monthly_result=$(check_monthly_costs)
        
        local monthly_cost
        monthly_cost=$(echo "$monthly_result" | cut -d',' -f1)
        
        local monthly_records
        monthly_records=$(echo "$monthly_result" | cut -d',' -f2)
        
        log "📊 Monthly cost: \$$(format_currency "$monthly_cost") (${monthly_records} records)"
        
        if (( $(echo "$monthly_cost > $MONTHLY_THRESHOLD" | bc -l) )); then
            monthly_exceeded=true
            log "${RED}⚠️  MONTHLY THRESHOLD EXCEEDED: \$$(format_currency "$monthly_cost") > \$${MONTHLY_THRESHOLD}${NC}"
            
            alert_messages+="🚨 Monthly Cost Alert

Current monthly cost: \$$(format_currency "$monthly_cost")
Threshold: \$${MONTHLY_THRESHOLD}
Records: ${monthly_records}

Top Services This Month:
$(get_service_breakdown "monthly")

"
        else
            log "${GREEN}✅ Monthly cost within threshold${NC}"
        fi
    fi
    
    # Send alerts if thresholds exceeded
    if [ "$daily_exceeded" = true ] || [ "$monthly_exceeded" = true ]; then
        send_alert "$alert_messages"
        
        log "${RED}❌ Billing check failed - thresholds exceeded${NC}"
        exit 1
    else
        log "${GREEN}✅ Billing check passed - all costs within thresholds${NC}"
        exit 0
    fi
}

# Help function
show_help() {
    echo "Sterling HA Billing Check Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [CHECK_TYPE]"
    echo ""
    echo "CHECK_TYPE:"
    echo "  daily     Check only daily costs"
    echo "  monthly   Check only monthly costs"
    echo "  both      Check both daily and monthly costs (default)"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GOOGLE_CLOUD_PROJECT      GCP Project ID (required)"
    echo "  BIGQUERY_DATASET          BigQuery dataset name (default: sterling_ha_analytics)"
    echo "  BILLING_EXPORT_TABLE      Billing export table name (default: billing_export)"
    echo "  DAILY_COST_THRESHOLD      Daily cost threshold (default: 2.00)"
    echo "  MONTHLY_COST_THRESHOLD    Monthly cost threshold (default: 50.00)"
    echo "  ALERT_EMAIL               Email address for alerts"
    echo ""
    echo "Examples:"
    echo "  $0                        # Check both daily and monthly costs"
    echo "  $0 daily                  # Check only daily costs"
    echo "  $0 monthly                # Check only monthly costs"
    echo ""
    echo "Exit Codes:"
    echo "  0  Success - all costs within thresholds"
    echo "  1  Failure - one or more thresholds exceeded"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    "")
        main "both"
        ;;
    daily|monthly|both)
        main "$1"
        ;;
    *)
        echo "Error: Invalid argument '$1'"
        echo "Use '$0 --help' for usage information"
        exit 1
        ;;
esac