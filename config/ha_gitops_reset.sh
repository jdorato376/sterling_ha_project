#!/bin/bash

# 🧹 Step 1: Stop Home Assistant Core
ha core stop

# 🧼 Step 2: Remove all config files and folders including hidden files
cd /config
rm -rf ./* .??*

# 📥 Step 3: Clone fresh repo from GitHub
git clone https://github.com/jdorato376/sterling_ha_project.git .

# ✅ Step 4: Touch .HA_VERSION to prevent HA complaints
touch .HA_VERSION

# 🚀 Step 5: Restart Home Assistant Core
ha core start

echo "✅ Fresh pull from GitHub complete. Home Assistant is now running the latest from sterling_ha_project."
