"""
Plaid Banking API Setup Script
Connects to your bank accounts through Plaid for automated financial tracking
"""

import os
import json
from datetime import datetime, timedelta
from plaid import ApiClient, Configuration
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest


class PlaidBankingClient:
    """
    Handles Plaid API authentication and banking operations
    Designed for sovereign financial infrastructure - your data, your control
    """
    
    def __init__(self, client_id=None, secret=None, environment='sandbox'):
        """
        Initialize Plaid client
        
        Args:
            client_id: Your Plaid client ID (from dashboard.plaid.com)
            secret: Your Plaid secret key
            environment: 'sandbox' for testing, 'development' or 'production' for real data
        """
        self.client_id = client_id or os.getenv('PLAID_CLIENT_ID')
        self.secret = secret or os.getenv('PLAID_SECRET')
        self.environment = environment
        
        if not self.client_id or not self.secret:
            raise ValueError("Must provide PLAID_CLIENT_ID and PLAID_SECRET")
        
        # Configure Plaid client
        configuration = Configuration(
            host=self._get_host(),
            api_key={
                'clientId': self.client_id,
                'secret': self.secret,
            }
        )
        
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
        
        # Storage for access tokens (in production, use encrypted database)
        self.access_tokens = {}
        self._load_tokens()
    
    def _get_host(self):
        """Get appropriate Plaid API host based on environment"""
        hosts = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }
        return hosts.get(self.environment, hosts['sandbox'])
    
    def _load_tokens(self):
        """Load saved access tokens from file"""
        token_file = 'plaid_tokens.json'
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                self.access_tokens = json.load(f)
    
    def _save_tokens(self):
        """Save access tokens to file (encrypt this in production)"""
        with open('plaid_tokens.json', 'w') as f:
            json.dump(self.access_tokens, f, indent=2)
    
    def create_link_token(self, user_id='user-1'):
        """
        Create a Link token for Plaid Link initialization
        This token is used in the web interface to connect banks
        
        Returns:
            dict with link_token and expiration
        """
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name='Ka\'tuar\'el Financial Infrastructure',
            products=[Products('transactions'), Products('auth')],
            country_codes=[CountryCode('US')],
            language='en'
        )
        
        response = self.client.link_token_create(request)
        return {
            'link_token': response['link_token'],
            'expiration': response['expiration']
        }
    
    def exchange_public_token(self, public_token, institution_name=None):
        """
        Exchange public token (from Plaid Link) for access token
        This is called after user completes bank connection in web interface
        
        Args:
            public_token: Token received from Plaid Link
            institution_name: Optional name to identify this bank
        
        Returns:
            access_token and item_id
        """
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Store the access token
        bank_id = institution_name or f"bank_{len(self.access_tokens) + 1}"
        self.access_tokens[bank_id] = {
            'access_token': access_token,
            'item_id': item_id,
            'connected_at': datetime.now().isoformat()
        }
        self._save_tokens()
        
        return {
            'access_token': access_token,
            'item_id': item_id,
            'bank_id': bank_id
        }
    
    def get_accounts(self, bank_id=None):
        """
        Retrieve all accounts for a connected bank
        
        Args:
            bank_id: Identifier for the bank (if None, returns all)
        
        Returns:
            List of account details
        """
        if bank_id and bank_id in self.access_tokens:
            banks_to_query = {bank_id: self.access_tokens[bank_id]}
        else:
            banks_to_query = self.access_tokens
        
        all_accounts = []
        
        for bank_id, token_data in banks_to_query.items():
            request = AccountsGetRequest(access_token=token_data['access_token'])
            response = self.client.accounts_get(request)
            
            for account in response['accounts']:
                all_accounts.append({
                    'bank_id': bank_id,
                    'account_id': account['account_id'],
                    'name': account['name'],
                    'type': account['type'],
                    'subtype': account['subtype'],
                    'balance': account['balances']['current'],
                    'currency': account['balances']['iso_currency_code']
                })
        
        return all_accounts
    
    def get_transactions(self, bank_id=None, days_back=30):
        """
        Retrieve transactions for connected accounts
        
        Args:
            bank_id: Specific bank to query (if None, queries all)
            days_back: How many days of transactions to retrieve
        
        Returns:
            List of transactions
        """
        start_date = (datetime.now() - timedelta(days=days_back)).date()
        end_date = datetime.now().date()
        
        if bank_id and bank_id in self.access_tokens:
            banks_to_query = {bank_id: self.access_tokens[bank_id]}
        else:
            banks_to_query = self.access_tokens
        
        all_transactions = []
        
        for bank_id, token_data in banks_to_query.items():
            request = TransactionsGetRequest(
                access_token=token_data['access_token'],
                start_date=start_date,
                end_date=end_date
            )
            response = self.client.transactions_get(request)
            
            for txn in response['transactions']:
                all_transactions.append({
                    'bank_id': bank_id,
                    'transaction_id': txn['transaction_id'],
                    'account_id': txn['account_id'],
                    'date': txn['date'],
                    'name': txn['name'],
                    'amount': txn['amount'],
                    'category': txn['category'],
                    'pending': txn['pending']
                })
        
        return sorted(all_transactions, key=lambda x: x['date'], reverse=True)


# Example usage and setup flow
def main():
    """
    Main setup flow for Plaid banking connection
    """
    print("=== Ka'tuar'el Financial Infrastructure Setup ===\n")
    
    # Initialize client (set environment variables first)
    # export PLAID_CLIENT_ID='your_client_id'
    # export PLAID_SECRET='your_secret'
    
    client = PlaidBankingClient(environment='sandbox')
    
    # Step 1: Create link token (use this in your web interface)
    print("Step 1: Creating Link token...")
    link_data = client.create_link_token()
    print(f"Link token: {link_data['link_token']}")
    print(f"Expires: {link_data['expiration']}\n")
    
    print("Use this link token to initialize Plaid Link in your web interface.")
    print("After connecting a bank, you'll receive a public_token.")
    print("Then call client.exchange_public_token(public_token) to get your access token.\n")
    
    # Step 2: Exchange public token (after user connects bank)
    # public_token = "public-sandbox-xxxxxx"  # This comes from Plaid Link
    # client.exchange_public_token(public_token, 'my_bank')
    
    # Step 3: Get accounts
    print("\nStep 3: Retrieving accounts...")
    accounts = client.get_accounts()
    for account in accounts:
        print(f"  {account['name']}: ${account['balance']} ({account['type']})")
    
    # Step 4: Get transactions
    print("\nStep 4: Retrieving recent transactions...")
    transactions = client.get_transactions(days_back=30)
    for txn in transactions[:10]:  # Show first 10
        print(f"  {txn['date']}: {txn['name']} - ${txn['amount']}")


if __name__ == '__main__':
    main()
