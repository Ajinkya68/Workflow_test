# filepath: tests/web/test_project_lifecycle.py
import pytest
import requests
import os
from playwright.sync_api import Page, expect
from appium import webdriver
from appium.options.common import AppiumOptions

def test_project_creation_and_isolation_flow(runtime_test_data, page: Page):
    """
    Validates complete transactional security boundaries:
    1. Creates project via backend API service layer.
    2. Validates dynamic visibility via Desktop Web layouts.
    3. Validates structural responsiveness rendering via BrowserStack Mobile.
    4. Validates tenant data separation constraints.
    """
    data = runtime_test_data
    
    # ------------------------------------------------------------------------
    # STEP 1: API - Provision Project
    # ------------------------------------------------------------------------
    api_url = "https://api.staging.workflowpro.com/api/v1/projects"
    headers = {
        "Authorization": f"Bearer {data['tenant_a']['token']}",
        "X-Tenant-ID": data['tenant_a']['id'],
        "Content-Type": "application/json"
    }
    payload = {
        "name": data["project_name"],
        "description": data["project_desc"],
        "team_members": ["admin@company1.com"]
    }
    
    response = requests.post(api_url, json=payload, headers=headers, timeout=10.0)
    assert response.status_code == 201, f"API Setup Crash: {response.text}"
    
    data["created_project_id"] = response.json()["id"]

    # ------------------------------------------------------------------------
    # STEP 2: Web UI - Verify Display (Tenant A Dashboard)
    # ------------------------------------------------------------------------
    page.goto(f"{data['tenant_a']['url']}/dashboard")
    page.wait_for_load_state("networkidle")
    
    # Auto-waiting validation pattern handles backend latency dynamically
    project_grid = page.locator(".project-list-grid")
    expect(project_grid).to_be_visible(timeout=8000)
    
    target_card = page.locator(f".project-card:has-text('{data['project_name']}')")
    expect(target_card).to_be_visible(timeout=5000)

    # ------------------------------------------------------------------------
    # STEP 3: Mobile - Check Cross-Platform Layout (BrowserStack)
    # ------------------------------------------------------------------------
    options = AppiumOptions()
    options.set_capability("browserName", "chrome")
    options.set_capability("deviceName", "Google Pixel 8")
    options.set_capability("os_version", "14.0")
    options.set_capability("realMobile", "true")
    options.set_capability("bstack:options", {
        "userName": os.getenv("BROWSERSTACK_USERNAME", "dummy_user"),
        "accessKey": os.getenv("BROWSERSTACK_ACCESS_KEY", "dummy_key")
    })

    mobile_driver = webdriver.Remote("http://hub.browserstack.com/wd/hub", options=options)
    try:
        mobile_driver.get(f"{data['tenant_a']['url']}/dashboard")
        mobile_driver.implicitly_wait(7.0)
        
        # Open mobile responsiveness panel if collapsed
        menu = mobile_driver.find_elements("css selector", "#mobile-nav-toggle")
        if menu:
            menu[0].click()
            
        mobile_card = mobile_driver.find_element(
            "xpath", f"//*[contains(@class, 'project-card') and contains(., '{data['project_name']}')]"
        )
        assert mobile_card.is_displayed(), "Responsive Error: Card not visible on mobile device viewport."
    finally:
        mobile_driver.quit()

    # ------------------------------------------------------------------------
    # STEP 4: Security - Verify Tenant Isolation (Tenant B Workspace Exclusion)
    # ------------------------------------------------------------------------
    page.goto(f"{data['tenant_b']['url']}/dashboard")
    page.wait_for_load_state("networkidle")
    
    expect(page.locator(".project-list-grid")).to_be_visible(timeout=7000)
    
    # Confirm unauthorized tenant card is completely hidden
    unauthorized_card = page.locator(f".project-card:has-text('{data['project_name']}')")
    expect(unauthorized_card).to_be_hidden(timeout=3000)