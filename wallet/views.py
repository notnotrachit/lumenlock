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
    print("Public Key: " + keypair.public_key)
    print("Secret Seed: " + keypair.secret)
    encryption_key = request.POST.get('password')
    encrypted_secret_seed = keypair.secret
    encrypted_secret_seed = cryptocode.encrypt(keypair.secret, encryption_key)
    wallet = Wallet.objects.create(
        user=User.objects.first(),
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