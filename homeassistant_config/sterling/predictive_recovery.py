import datetime
import json
import os

from .audit_logger import log_event

BACKUP_PATH = "/config/sterling/backups/"
CONFIG_FILE = "/config/configuration.yaml"


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def create_backup() -> str | None:
    os.makedirs(BACKUP_PATH, exist_ok=True)
    backup_file = os.path.join(BACKUP_PATH, f"config_backup_{timestamp()}.yaml")
    try:
        os.system(f"cp {CONFIG_FILE} {backup_file}")
        log_event(f"✅ Created backup: {backup_file}")
        return backup_file
    except Exception as e:
        log_event(f"❌ Backup failed: {str(e)}")
        return None


def validate_config() -> bool:
    result = os.system(
        "docker run -v /config:/config --rm ghcr.io/home-assistant/home-assistant:stable --script check_config"
    )
    return result == 0


def auto_repair() -> bool:
    log_event("🛠 Attempting auto-repair via backup rollback...")
    backups = sorted(os.listdir(BACKUP_PATH), reverse=True)
    if backups:
        latest = backups[0]
        os.system(f"cp {os.path.join(BACKUP_PATH, latest)} {CONFIG_FILE}")
        log_event(f"🔁 Restored from backup: {latest}")
        return True
    log_event("❌ No backups available to restore")
    return False


def predictive_validate_and_recover() -> None:
    create_backup()
    if validate_config():
        log_event("✅ Configuration is valid. No recovery needed.")
    else:
        log_event("⚠️ Configuration is invalid. Attempting recovery...")
        auto_repair()
