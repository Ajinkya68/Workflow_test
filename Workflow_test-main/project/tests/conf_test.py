# filepath: tests/conftest.py
import pytest
import os
import requests
import uuid
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def execution_settings():
    """Extracts execution parameters dynamically from system environments."""
    return {
        "env": os.getenv("TEST_ENV", "staging"),
        "base_domain": os.getenv("BASE_DOMAIN", "workflowpro.com"),
        "execution_target": os.getenv("EXECUTION_TARGET", "local")
    }

@pytest.fixture(scope="function")
def runtime_test_data(execution_settings):
    """
    Generates isolated, unique data contexts for parallel execution runs.
    Cleans up created assets systematically during the teardown sweep.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    data_blueprint = {
        "project_name": f"QA_Integration_Project_{unique_suffix}",
        "project_desc": "Automated verification benchmark container.",
        "created_project_id": None,
        "tenant_a": {
            "id": "company1",
            "token": os.getenv("COMPANY1_API_TOKEN", "mock_jwt_token_t1"),
            "url": f"https://company1.staging.{execution_settings['base_domain']}"
        },
        "tenant_b": {
            "id": "company2",
            "token": os.getenv("COMPANY2_API_TOKEN", "mock_jwt_token_t2"),
            "url": f"https://company2.staging.{execution_settings['base_domain']}"
        }
    }
    
    yield data_blueprint

    # --- TEARDOWN SWEEP ---
    if data_blueprint["created_project_id"]:
        cleanup_url = f"https://api.staging.{execution_settings['base_domain']}/api/v1/projects/{data_blueprint['created_project_id']}"
        headers = {
            "Authorization": f"Bearer {data_blueprint['tenant_a']['token']}",
            "X-Tenant-ID": data_blueprint['tenant_a']['id']
        }
        try:
            requests.delete(cleanup_url, headers=headers, timeout=5.0)
        except requests.exceptions.RequestException:
            pass