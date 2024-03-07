# LumenLock

A simple custodial wallet for Lumen (XLM) built using Django and the Stellar SDK.

This is a very secure wallet. Once a user creates a new wallet, he/she sets a transaction password. The transaction password is never stored in the database. That is used to encrypt the wallet secret seed and then stored in the backend. Even the admins won't be able to access your wallet. 

## Installation

1. Clone the repository: `git clone https://github.com/notnotrachit/lumenlock`
2. Install the dependencies: `pip install -r requirements.txt`
3. Apply database migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`
