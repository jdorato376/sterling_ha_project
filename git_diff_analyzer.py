import subprocess
import json
import os


def get_last_commit_diff():
    """Extract git diff of the last commit and return structured JSON."""
    try:
        diff_output = subprocess.check_output(
            ['git', 'diff', 'HEAD~1', 'HEAD', '--unified=0'],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        changes = {"added": [], "removed": [], "modified": []}
        current_file = None
        for line in diff_output.splitlines():
            if line.startswith('+++ b/'):
                current_file = line[6:]
            elif line.startswith('@@'):
                continue
            elif line.startswith('+') and not line.startswith('+++'):
                changes['added'].append({"file": current_file, "line": line[1:].strip()})
            elif line.startswith('-') and not line.startswith('---'):
                changes['removed'].append({"file": current_file, "line": line[1:].strip()})
        modified_files = list({c['file'] for c in changes['added'] + changes['removed']})
        changes['modified'] = modified_files
        log_dir = 'logs'
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            pass
        with open(f"{log_dir}/git_delta_log.json", 'w') as f:
            json.dump(changes, f, indent=2)
        return changes
    except subprocess.CalledProcessError as e:
        return {"error": f"Git diff failed: {e.output.decode('utf-8')}"}
