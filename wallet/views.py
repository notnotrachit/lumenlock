from django.shortcuts import render
from django.http import JsonResponse
from stellar_sdk import Asset, Server, Keypair, TransactionBuilder, Network
from stellar_sdk.exceptions import Ed25519SecretSeedInvalidError, NotFoundError
from .models import Wallet
import cryptocode
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
import logging
from ratelimit.decorators import ratelimit
from django.contrib import messages
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException, Timeout
from django.db import IntegrityError

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

@ratelimit(key='user', rate='3/m', method='POST', block=True)
@login_required
def create_wallet(request):
    if Wallet.objects.filter(user=request.user).exists():
        return redirect('dashboard')
    
    encryption_key = request.POST.get('password')
    if not encryption_key or len(encryption_key) < 8:
        messages.error(request, 'Password must be at least 8 characters long.')
        return redirect('dashboard')
    
    try:
        keypair = Keypair.random()
        encrypted_secret_seed = cryptocode.encrypt(keypair.secret, encryption_key)
        
        wallet = Wallet.objects.create(
            user=request.user,  # Fixed: use actual user instead of first user
            public_key=keypair.public_key,
            secret_seed=encrypted_secret_seed
        )
        
        # Fund the account on testnet
        url = "https://friendbot.stellar.org"
        try:
            response = requests.get(url, params={"addr": keypair.public_key}, timeout=10)
            response.raise_for_status()
            logger.info(f'Wallet created successfully for user {request.user.username}')
            messages.success(request, 'Wallet created successfully!')
        except (RequestException, Timeout) as e:
            logger.error(f'Failed to fund account for user {request.user.username}: {str(e)}')
            messages.warning(request, 'Wallet created but funding failed. Contact support.')
            
    except IntegrityError:
        logger.error(f'Wallet creation failed - integrity error for user {request.user.username}')
        messages.error(request, 'Wallet creation failed. Please try again.')
    except Exception as e:
        logger.error(f'Unexpected error creating wallet for user {request.user.username}: {str(e)}')
        messages.error(request, 'An unexpected error occurred.')
    
    return redirect('dashboard')


@ratelimit(key='user', rate='10/m', method='POST', block=True)
@login_required
def check_balance(request):
    public_key = request.POST.get('public_key')
    
    if not public_key:
        try:
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                return JsonResponse({'error': 'No wallet found for user'}, status=404)
            public_key = wallet.public_key
        except Exception as e:
            logger.error(f'Error retrieving wallet for user {request.user.username}: {str(e)}')
            return JsonResponse({'error': 'Failed to retrieve wallet'}, status=500)
    
    try:
        server = Server("https://horizon-testnet.stellar.org")
        account = server.accounts().account_id(public_key).call()
        
        if account.get('balances') and len(account['balances']) > 0:
            balance = account['balances'][0]['balance']
            return JsonResponse({'balance': balance})
        else:
            return JsonResponse({'error': 'No balance information available'}, status=404)
            
    except NotFoundError:
        logger.warning(f'Account not found for public key: {public_key}')
        return JsonResponse({'error': 'Account not found'}, status=404)
    except Exception as e:
        logger.error(f'Error checking balance for {public_key}: {str(e)}')
        return JsonResponse({'error': 'Failed to check balance'}, status=500)


@ratelimit(key='user', rate='5/m', method='POST', block=True)
@login_required
def send_money(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            destination_public_key = data.get('recipient')
            amount = data.get('amount')
            encryption_key = data.get('transaction_password')
            
            # Input validation
            if not destination_public_key or not amount or not encryption_key:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Validate amount
            try:
                amount_float = float(amount)
                if amount_float <= 0:
                    return JsonResponse({'error': 'Amount must be positive'}, status=400)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid amount format'}, status=400)
            
            # Get user wallet safely
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                return JsonResponse({'error': 'No wallet found'}, status=404)
            
            server = Server("https://horizon-testnet.stellar.org")
            
            try:
                # Decrypt secret key
                decrypted_secret = cryptocode.decrypt(wallet.secret_seed, encryption_key)
                if not decrypted_secret:
                    return JsonResponse({'error': 'Invalid transaction password'}, status=401)
                
                source_keypair = Keypair.from_secret(decrypted_secret)
            except (Ed25519SecretSeedInvalidError, ValueError):
                logger.warning(f'Invalid transaction password for user {request.user.username}')
                return JsonResponse({'error': 'Invalid transaction password'}, status=401)
            
            # Load accounts and build transaction
            try:
                destination_account = server.load_account(destination_public_key)
                source_account = server.load_account(source_keypair.public_key)
                
                transaction = TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                    base_fee=100
                ).append_payment_op(
                    destination=destination_public_key,
                    amount=str(amount_float),
                    asset=Asset.native()
                ).set_timeout(30).build()
                
                transaction.sign(source_keypair)
                response = server.submit_transaction(transaction)
                
                logger.info(f'Payment sent successfully from {request.user.username} to {destination_public_key}')
                return JsonResponse({
                    'message': 'Payment sent successfully', 
                    'status': 'success',
                    'transaction_hash': response.get('hash')
                })
                
            except NotFoundError as e:
                logger.error(f'Account not found in send_money: {str(e)}')
                return JsonResponse({'error': 'Destination account not found'}, status=404)
            except Exception as e:
                logger.error(f'Transaction failed for user {request.user.username}: {str(e)}')
                return JsonResponse({'error': 'Transaction failed'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f'Unexpected error in send_money for user {request.user.username}: {str(e)}')
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def dashboard(request):
    wallet_exists = Wallet.objects.filter(user=request.user).exists()
    if not wallet_exists:
        return render(request, 'dashboard.html', {'wallet_exists': wallet_exists})
    
    try:
        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return render(request, 'dashboard.html', {'wallet_exists': False})
        
        server = Server("https://horizon-testnet.stellar.org")
        account = server.accounts().account_id(wallet.public_key).call()
        
        balance = '0'
        if account.get('balances') and len(account['balances']) > 0:
            balance = account['balances'][0]['balance']
        
        context = {
            'wallet_exists': wallet_exists,
            'balance': balance,
            'public_key': wallet.public_key
        }
        return render(request, 'dashboard.html', context)
        
    except NotFoundError:
        logger.warning(f'Account not found for wallet {wallet.public_key}')
        context = {
            'wallet_exists': wallet_exists,
            'balance': '0',
            'public_key': wallet.public_key,
            'error': 'Account not found on network'
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logger.error(f'Error loading dashboard for user {request.user.username}: {str(e)}')
        context = {
            'wallet_exists': wallet_exists,
            'balance': 'Error',
            'public_key': wallet.public_key if wallet else '',
            'error': 'Failed to load wallet information'
        }
        return render(request, 'dashboard.html', context)