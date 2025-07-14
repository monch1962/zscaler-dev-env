#!/usr/bin/env python3
# zscaler_api_test.py
import os
from zscaler import ZscalerClient
from pprint import pprint

# --- Configuration for Authentication (Choose OneAPI or Legacy) ---
# Set ZSCALER_USE_LEGACY_CLIENT="true" in your environment to use Legacy API auth.
# Otherwise, OneAPI (OAuth2) will be attempted.

USE_LEGACY_CLIENT = os.getenv("ZSCALER_USE_LEGACY_CLIENT", "false").lower() == "true"

# Common Zscaler Cloud Name (e.g., "zscalerone", "zscalertwo", "zscloud", "zscaler.net", etc.)
# This is usually the part after 'admin.' in your ZIA admin URL.
ZSCALER_CLOUD = os.getenv("ZSCALER_CLOUD")

# ZIA Legacy API Credentials (if USE_LEGACY_CLIENT is true)
ZIA_USERNAME = os.getenv("ZIA_USERNAME")
ZIA_PASSWORD = os.getenv("ZIA_PASSWORD")
ZIA_API_KEY = os.getenv("ZIA_API_KEY")

# OneAPI (OAuth2) Credentials (if USE_LEGACY_CLIENT is false)
ZSCALER_CLIENT_ID = os.getenv("ZSCALER_CLIENT_ID")
ZSCALER_CLIENT_SECRET = os.getenv("ZSCALER_CLIENT_SECRET")
# ZSCALER_VANITY_DOMAIN is optional for OneAPI, but good practice if applicable
ZSCALER_VANITY_DOMAIN = os.getenv("ZSCALER_VANITY_DOMAIN")

def get_zia_client():
    """
    Initializes and returns a ZIA client based on environment variables.
    Prioritizes OneAPI (OAuth2) if ZSCALER_USE_LEGACY_CLIENT is not "true".
    """
    if USE_LEGACY_CLIENT:
        if not all([ZIA_USERNAME, ZIA_PASSWORD, ZIA_API_KEY, ZSCALER_CLOUD]):
            print("Error: For Legacy API, ZIA_USERNAME, ZIA_PASSWORD, ZIA_API_KEY, and ZSCALER_CLOUD must be set.")
            raise ValueError("Missing Legacy API credentials.")
        print("Initializing ZIA client with Legacy API (username/password/API Key)...")
        return ZscalerClient(
            cloud=ZSCALER_CLOUD,
            username=ZIA_USERNAME,
            password=ZIA_PASSWORD,
            api_key=ZIA_API_KEY,
            # Explicitly tell the SDK to use the legacy client for ZIA if needed
            # zia_client_type='legacy'
        ).zia
    else:
        if not all([ZSCALER_CLIENT_ID, ZSCALER_CLIENT_SECRET, ZSCALER_CLOUD]):
            print("Error: For OneAPI, ZSCALER_CLIENT_ID, ZSCALER_CLIENT_SECRET, and ZSCALER_CLOUD must be set.")
            raise ValueError("Missing OneAPI credentials.")
        print("Initializing ZIA client with OneAPI (OAuth2)...")
        return ZscalerClient(
            client_id=ZSCALER_CLIENT_ID,
            client_secret=ZSCALER_CLIENT_SECRET,
            cloud=ZSCALER_CLOUD,
            vanity_domain=ZSCALER_VANITY_DOMAIN # Optional
        ).zia

try:
    zia = get_zia_client()

    print("\nFetching users from ZIA test tenant...")
    # The SDK's methods might have changed slightly; check current docs for exact calls.
    # .users.list_users() is generally stable, but verify if issues arise.
    users = zia.users.list_users()
    pprint(users)
    print(f"Successfully fetched {len(users)} users.")

    # --- Example: URL Category Management ---
    new_category_name = "hoverfly_test_category_1"

    print(f"\nAttempting to manage URL category: '{new_category_name}'")
    try:
        # Check if category already exists to avoid errors on re-run
        # The list_url_categories method might support 'search' or similar filtering
        # Consult Zscaler SDK docs for precise filtering arguments.
        existing_categories = zia.url_categories.list_url_categories()
        existing_category = next((c for c in existing_categories if c.get('configuredName') == new_category_name), None)

        if existing_category:
            print(f"URL category '{new_category_name}' already exists.")
            pprint(existing_category)
            # You could add an update operation here if needed
            # print("Attempting to update existing category...")
            # update_payload = {"urls": ["updated.example.com"]}
            # updated_category = zia.url_categories.update_url_category(existing_category['id'], update_payload)
            # pprint(updated_category)

            # Or delete it for a clean run next time:
            print(f"Deleting existing category '{new_category_name}' (ID: {existing_category['id']})...")
            zia.url_categories.delete_url_category(existing_category['id'])
            print(f"Successfully deleted URL category '{new_category_name}'.")
            # After deletion, we might want to re-attempt creation
            existing_category = None # Reset to allow creation logic to run

        if not existing_category: # If it didn't exist or was just deleted
            print(f"Creating new URL category: '{new_category_name}'...")
            new_category_payload = {
                "configuredName": new_category_name,
                "urls": ["example.com", "test.org"],
                "type": "CUSTOM",
                "scope": "ORGANIZATION",
                "description": "Created by Zscaler SDK Python for Hoverfly capture"
            }
            created_category = zia.url_categories.add_url_category(new_category_payload)
            print(f"Successfully created URL category: {created_category.get('configuredName')}")
            pprint(created_category)

    except Exception as e:
        print(f"Error during URL category operation: {e}")
        # Print a more detailed error if possible
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"API Response Error: {e.response.text}")
        elif hasattr(e, 'message'):
            print(f"Error message: {e.message}")

    # For ZIA, remember to activate changes if necessary.
    # The activation process might involve a call like:
    # print("\nActivating pending changes (if any)...")
    # zia.admin.activate() # Or similar, check SDK documentation
    # print("Changes activated.")


except Exception as e:
    print(f"\nAn error occurred during Zscaler API client initialization or main operation: {e}")
    if hasattr(e, 'response') and hasattr(e.response, 'text'):
        print(f"API Response Error: {e.response.text}")
