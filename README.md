# LumenLock

![Logo](logo.jpg)

A simple custodial wallet for Lumen (XLM) built using Django and the Stellar SDK.

This is a very secure wallet. Once a user creates a new wallet, he/she sets a transaction password. The transaction password is never stored in the database. That is used to encrypt the wallet secret seed and then stored in the backend. Even the admins won't be able to access your wallet. 


## Project Details
**LumenLock** is a secure custodial wallet designed for storing and managing Lumen (XLM) tokens. Developed on the Stellar Blockchain using Django framework and the Stellar SDK, LumenLock provides users with a straightforward and reliable platform for securely holding their XLM assets. The platform offers essential wallet functionalities, including receiving and sending of Lumens, with robust security measures in place to safeguard user funds. Users can easily access their accounts, monitor transactions, and manage their XLM holdings through a user-friendly interface. LumenLock prioritizes simplicity and security, ensuring a seamless user experience while maintaining the integrity and decentralization inherent in blockchain technology. With its focus on ease of use and security, LumenLock aims to become the go-to custodial wallet solution for Stellar users seeking a reliable platform to manage their XLM assets.

## Vision
Our vision for LumenLock is to revolutionize the way users interact with their Stellar Lumens (XLM) by providing a secure, user-friendly custodial wallet solution. By simplifying the management of XLM assets and ensuring robust security measures, we aim to empower individuals and businesses to confidently engage with the Stellar Blockchain. LumenLock will not only enhance accessibility to XLM, but also contribute to the widespread adoption of blockchain technology by offering a seamless and trustworthy platform for users to store and manage their digital assets. Our goal is to become the leading custodial wallet solution for the Stellar community, driving innovation and facilitating financial inclusion.

## Development Plan
- Smart Contract Development:
    Define smart contract structure for user accounts, transactions, and security.
    Implement functions for deposit, withdrawal, and transfer of Lumens (XLM).
    Integrate security measures like multi-signature authentication and event logging.

- Front-End Development:
    Design user interface for registration, login, and dashboard.
    Create intuitive forms for XLM transactions.
    Ensure real-time updates for account balances and transaction status.

- Testing:
    Conduct integration testing for smart contract and front-end.
    Perform user acceptance testing for feedback.
    Conduct security audit to address vulnerabilities.

- Deployment:
    Finalize development, testing, and security measures.
    Deploy smart contract and front-end to secure hosting.
    Monitor deployment for any issues.

## Installation

1. Clone the repository: `git clone https://github.com/notnotrachit/lumenlock`
2. Install the dependencies: `pip install -r requirements.txt`
3. Apply database migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`