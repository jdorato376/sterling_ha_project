#!/usr/bin/env python3
"""
Validate Home Assistant Add-on Configuration
"""

import json
import sys
from pathlib import Path

def validate_addons_json():
    """Validate the repository addons.json file"""
    try:
        with open('addons.json', 'r') as f:
            addons_config = json.load(f)
        
        required_fields = ['name', 'url', 'maintainer', 'addons']
        for field in required_fields:
            if field not in addons_config:
                print(f"❌ addons.json missing required field: {field}")
                return False
        
        print("✅ addons.json validation passed")
        return True
    except Exception as e:
        print(f"❌ addons.json validation failed: {e}")
        return False

def validate_addon_config():
    """Validate the add-on config.json file"""
    try:
        config_path = Path('addons/sterling_os/config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Required fields for Home Assistant add-ons
        required_fields = ['name', 'version', 'slug', 'description', 'startup', 'boot']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ config.json missing required fields: {missing_fields}")
            return False
        
        # Check version format
        version = config.get('version', '')
        if not version or not any(c.isdigit() for c in version):
            print(f"❌ config.json has invalid version format: {version}")
            return False
        
        # Check startup values
        valid_startup = ['before', 'after', 'once', 'services', 'system', 'application']
        if config.get('startup') not in valid_startup:
            print(f"❌ config.json has invalid startup value: {config.get('startup')}")
            return False
        
        # Check boot values  
        valid_boot = ['auto', 'manual']
        if config.get('boot') not in valid_boot:
            print(f"❌ config.json has invalid boot value: {config.get('boot')}")
            return False
        
        print("✅ config.json validation passed")
        return True
        
    except Exception as e:
        print(f"❌ config.json validation failed: {e}")
        return False

def validate_file_structure():
    """Validate that required files exist with correct permissions"""
    checks = []
    
    # Check required files exist
    required_files = [
        'addons.json',
        'addons/sterling_os/config.json',
        'addons/sterling_os/Dockerfile',
        'addons/sterling_os/README.md',
        'addons/sterling_os/run.sh',
        'LICENSE'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Missing required file: {file_path}")
            checks.append(False)
        else:
            checks.append(True)
    
    # Check shell scripts have execute permissions
    shell_scripts = [
        'addons/sterling_os/run.sh',
        'addons/sterling_os/entrypoint.sh',
        'build_addon.sh'
    ]
    
    for script_path in shell_scripts:
        path = Path(script_path)
        if path.exists():
            import os
            if not os.access(path, os.X_OK):
                print(f"❌ Script missing execute permission: {script_path}")
                checks.append(False)
            else:
                checks.append(True)
    
    if all(checks):
        print("✅ File structure validation passed")
        return True
    else:
        print("❌ File structure validation failed")
        return False

def main():
    """Run all validations"""
    print("🔍 Validating Home Assistant Add-on Configuration...")
    print()
    
    results = [
        validate_addons_json(),
        validate_addon_config(), 
        validate_file_structure()
    ]
    
    print()
    if all(results):
        print("🎉 All validations passed! Your add-on is ready for Home Assistant.")
        sys.exit(0)
    else:
        print("💥 Some validations failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()