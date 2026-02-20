from django.shortcuts import render
from django.http import JsonResponse
from stellar_sdk import Asset, Server, Keypair, TransactionBuilder, Network
from .models import Wallet
import cryptocode
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json

def home(request):
    return render(request, 'home.html')

@login_required
def create_wallet(request):
    if Wallet.objects.filter(user=request.user).exists():
        return redirect('dashboard')
    keypair = Keypair.random()
    encryption_key = request.POST.get('password')
    encrypted_secret_seed = keypair.secret
    encrypted_secret_seed = cryptocode.encrypt(keypair.secret, encryption_key)
    wallet = Wallet.objects.create(
        user=request.user,
        public_key=keypair.public_key,
        secret_seed=encrypted_secret_seed
    )
    url = "https://friendbot.stellar.org"
    response = requests.get(url, params={"addr": keypair.public_key})
    return redirect('dashboard')


def check_balance(request):
    public_key = request.POST.get('public_key')
    if not public_key:
        wallet = Wallet.objects.filter(user=request.user)[0]
        public_key = wallet.public_key
    server = Server("https://horizon-testnet.stellar.org")
    account = server.accounts().account_id(public_key).call()
    return JsonResponse({'balance': account['balances'][0]['balance']})


@login_required
def send_money(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        destination_public_key = data.get('recipient')
        amount = data.get('amount')
        encryption_key = data.get('transaction_password')
        wallet = Wallet.objects.filter(user=request.user)[0]
        server = Server("https://horizon-testnet.stellar.org")
        source_keypair = Keypair.from_secret(cryptocode.decrypt(wallet.secret_seed, encryption_key))
        destination_account = server.load_account(destination_public_key)
        transaction = TransactionBuilder(
            source_account=server.load_account(source_keypair.public_key),
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        ).append_payment_op(
            destination=destination_public_key,
            amount=amount,
            asset=Asset.native()
        ).set_timeout(30).build()
        transaction.sign(source_keypair)
        response = server.submit_transaction(transaction)
        return JsonResponse({'message': 'Payment sent successfully', 'status': 'success'})
    else:
        pass


@login_required
def transaction_history(request):
    wallet = Wallet.objects.filter(user=request.user).first()
    if not wallet:
        return JsonResponse({'error': 'No wallet found'}, status=404)

    server = Server("https://horizon-testnet.stellar.org")
    try:
        transactions = (
            server.transactions()
            .for_account(wallet.public_key)
            .order(desc=True)
            .limit(10)
            .call()
        )
        records = transactions.get('_embedded', {}).get('records', [])
        history = []
        for tx in records:
            history.append({
                'id': tx.get('id', ''),
                'created_at': tx.get('created_at', ''),
                'source_account': tx.get('source_account', ''),
                'fee_charged': tx.get('fee_charged', ''),
                'operation_count': tx.get('operation_count', 0),
                'memo': tx.get('memo', '—'),
                'successful': tx.get('successful', False),
            })
        return JsonResponse({'transactions': history})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard(request):
    wallet_exists = Wallet.objects.filter(user=request.user).exists()
    if not wallet_exists:
        return render(request, 'dashboard.html', {'wallet_exists': wallet_exists})
    wallet = Wallet.objects.filter(user=request.user)[0]
    server = Server("https://horizon-testnet.stellar.org")
    account = server.accounts().account_id(wallet.public_key).call()
    balance = account['balances'][0]['balance']
    context = {
        'wallet_exists': wallet_exists,
        'balance': balance,
        'public_key': wallet.public_key
    }
    return render(request, 'dashboard.html', context)