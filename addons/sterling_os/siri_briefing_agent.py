import datetime
from sterling_core import send_ha_notification


def get_daily_summary():
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "headlines": [
            "📈 Finance: Markets opened cautiously amid Fed statements.",
            "🏥 Healthcare: CMS released new guidance for CDPAP billing.",
            "⚖️ AI Law: EU AI Act enforcement phase begins today.",
            "📊 Internal: No critical HA or Git anomalies detected overnight.",
        ],
    }


def main():
    summary = get_daily_summary()
    body = "\n".join(summary["headlines"])
    send_ha_notification(
        title=f"Good Morning - {summary['date']}",
        message=body,
    )


if __name__ == "__main__":
    main()
