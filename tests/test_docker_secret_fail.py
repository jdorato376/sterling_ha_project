import os
import yaml

WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows', 'docker-publish.yml')

def test_docker_workflow_removed():
    """Ensure deprecated docker workflow has been removed."""
    assert not os.path.exists(WORKFLOW_PATH)
