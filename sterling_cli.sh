#!/bin/bash
case "" in
  sync) python3 addons/sterling_os/ha_gitops_sync.py;;
  status) tail addons/sterling_os/logs/audit_log.json;;
  escalate) echo "🚨 Escalation triggered via CLI";;
esac
