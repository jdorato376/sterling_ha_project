import os
import yaml

WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows', 'docker-publish.yml')

def test_docker_secrets_present():
    with open(WORKFLOW_PATH) as f:
        data = yaml.safe_load(f)
    steps = data['jobs']['build']['steps']
    login = next(s for s in steps if s.get('uses', '').startswith('docker/login-action'))
    assert login['with']['username'] == '${{ secrets.DOCKER_USERNAME }}'
    assert login['with']['password'] == '${{ secrets.DOCKER_PASSWORD }}'
