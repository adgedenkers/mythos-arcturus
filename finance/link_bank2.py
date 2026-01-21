#!/usr/bin/env python3
"""
Mythos Finance - Bank Linking Script (Reliable Method)
Uses Plaid's hosted Link flow
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
import plaid
from plaid.api_client import ApiClient
from plaid.configuration import Configuration

# Load environment variables
load_dotenv('/opt/mythos/.env')

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

# Database configuration
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

# Cloudflare tunnel callback
REDIRECT_URI = 'https://mythos-api.denkers.co/plaid/callback'

# Validate configuration
if not PLAID_CLIENT_ID or not PLAID_SECRET:
    print("Error: PLAID_CLIENT_ID and PLAID_SECRET must be set in /opt/mythos/.env")
    sys.exit(1)

# Configure Plaid client
configuration = Configuration(
    host='https://production.plaid.com',
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def get_db_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_link_token():
    """Create a Plaid Link token"""
    try:
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Mythos Finance",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id='user-' + datetime.now().strftime('%Y%m%d%H%M%S')
            ),
            redirect_uri=REDIRECT_URI
        )
        
        response = client.link_token_create(request)
        return response['link_token']
    
    except plaid.ApiException as e:
        print(f"Error creating link token: {e}")
        print(f"Response body: {e.body}")
        sys.exit(1)

def exchange_public_token(pub_token):
    """Exchange public token for access token"""
    try:
        request = ItemPublicTokenExchangeRequest(
            public_token=pub_token
        )
        
        response = client.item_public_token_exchange(request)
        return response['access_token'], response['item_id']
    
    except plaid.ApiException as e:
        print(f"Error exchanging token: {e}")
        sys.exit(1)

def get_accounts(access_token):
    """Get account information from Plaid"""
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        return response['accounts'], response['item']
    
    except plaid.ApiException as e:
        print(f"Error getting accounts: {e}")
        sys.exit(1)

def save_to_database(item_id, access_token, institution_id, institution_name, accounts):
    """Save institution and accounts to database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Insert institution
        cur.execute("""
            INSERT INTO institutions (item_id, access_token, institution_id, institution_name, status, last_successful_sync)
            VALUES (%s, %s, %s, %s, 'active', NOW())
            RETURNING id
        """, (item_id, access_token, institution_id, institution_name))
        
        institution_db_id = cur.fetchone()[0]
        
        # Insert accounts
        for account in accounts:
            cur.execute("""
                INSERT INTO accounts (
                    institution_id, 
                    plaid_account_id, 
                    name, 
                    official_name,
                    account_type,
                    account_subtype,
                    mask,
                    current_balance,
                    available_balance,
                    limit_balance,
                    currency,
                    is_active,
                    last_balance_update
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                institution_db_id,
                account['account_id'],
                account['name'],
                account.get('official_name'),
                account['type'],
                account['subtype'],
                account.get('mask'),
                account['balances']['current'],
                account['balances'].get('available'),
                account['balances'].get('limit'),
                account['balances']['iso_currency_code'],
                True
            ))
        
        conn.commit()
        return institution_db_id
    
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        cur.close()
        conn.close()

def main():
    print("=" * 70)
    print("MYTHOS FINANCE - Bank Linking")
    print("=" * 70)
    print()
    
    # Create link token
    print("Creating Plaid Link token...")
    link_token = create_link_token()
    print("Link token created!")
    print()
    
    print("=" * 70)
    print("STEP 1: Open Plaid Link")
    print("=" * 70)
    print()
    print("Visit this URL in your browser:")
    print()
    print(f"https://my.plaid.com/link/?key={PLAID_CLIENT_ID}&token={link_token}")
    print()
    print("Or copy this simpler URL:")
    print()
    # Create a simple HTML file locally for them to open
    html_file = "/tmp/plaid_link.html"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mythos Finance - Link Bank</title>
    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
</head>
<body style="font-family: Arial; padding: 50px; text-align: center;">
    <h1>Click to Link Your Bank</h1>
    <button id="link-button" style="
        background: #10b981;
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 18px;
        border-radius: 8px;
        cursor: pointer;
    ">Connect Bank Account</button>
    
    <script>
    const linkHandler = Plaid.create({{
        token: '{link_token}',
        onSuccess: (public_token, metadata) => {{
            document.body.innerHTML = '<div style="padding: 50px;"><h1 style="color: #10b981;">Success!</h1><p>Copy this token:</p><div style="background: #f0f0f0; padding: 20px; margin: 20px; border-radius: 8px; word-break: break-all; font-family: monospace;">' + public_token + '</div><p>Paste it into your terminal.</p></div>';
        }},
        onExit: (err, metadata) => {{
            if (err != null) {{
                alert('Error: ' + err);
            }}
        }}
    }});
    
    document.getElementById('link-button').addEventListener('click', () => {{
        linkHandler.open();
    }});
    </script>
</body>
</html>"""
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"file://{html_file}")
    print()
    print("(HTML file saved - you can open it in your browser)")
    print()
    
    print("=" * 70)
    print("STEP 2: Complete Bank Linking")
    print("=" * 70)
    print()
    print("  1. Search for your bank")
    print("  2. Login with your credentials")
    print("  3. Select accounts to link")
    print("  4. Copy the public_token displayed")
    print()
    
    # Get public token from user
    public_token = input("Paste the public_token here: ").strip()
    
    if not public_token or not public_token.startswith('public-'):
        print()
        print("Error: Invalid public token. It should start with 'public-'")
        sys.exit(1)
    
    print()
    print("Token received!")
    print()
    
    # Exchange for access token
    print("Exchanging public token for access token...")
    access_token, item_id = exchange_public_token(public_token)
    print("Access token obtained!")
    print()
    
    # Get account information
    print("Retrieving account information...")
    accounts, item_info = get_accounts(access_token)
    
    institution_id = item_info['institution_id']
    institution_name = item_info.get('institution_name', 'Unknown Bank')
    
    print(f"Found {len(accounts)} account(s) at {institution_name}")
    print()
    
    # Display accounts
    print("Accounts found:")
    total_balance = 0
    for account in accounts:
        balance = account['balances']['current'] or 0
        total_balance += balance
        avail = account['balances'].get('available', balance)
        print(f"  - {account['name']} (...{account.get('mask', '????')})")
        print(f"    Current: ${balance:,.2f}")
        if avail != balance:
            print(f"    Available: ${avail:,.2f}")
    print()
    print(f"Total: ${total_balance:,.2f}")
    print()
    
    # Save to database
    print("Saving to database...")
    institution_db_id = save_to_database(item_id, access_token, institution_id, institution_name, accounts)
    print("Saved successfully!")
    print()
    
    print("=" * 70)
    print("SUCCESS - Bank Linked!")
    print("=" * 70)
    print()
    print(f"Institution: {institution_name}")
    print(f"Accounts: {len(accounts)}")
    print(f"Database ID: {institution_db_id}")
    print()
    print("Next steps:")
    print("  1. Link your other 3 banks (run this script 3 more times)")
    print("  2. Start the automated sync service")
    print()

if __name__ == '__main__':
    main()
