from django.shortcuts import render
from django.http import JsonResponse
from stellar_sdk import Asset, Server, Keypair, TransactionBuilder, Network
from .models import Wallet
import cryptocode
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import requests



def home(request):
    return render(request, 'home.html')


def create_wallet(request):
    keypair = Keypair.random()
    print("Public Key: " + keypair.public_key)
    print("Secret Seed: " + keypair.secret)
    encryption_key = "Hello"
    encrypted_secret_seed = keypair.secret
    encrypted_secret_seed = cryptocode.encrypt(keypair.secret, encryption_key)
    wallet = Wallet.objects.create(
        user=User.objects.first(),
        public_key=keypair.public_key,
        secret_seed=encrypted_secret_seed
    )
    url = "https://friendbot.stellar.org"
    response = requests.get(url, params={"addr": keypair.public_key})
    return JsonResponse({'public_key': keypair.public_key, 'secret_seed': keypair.secret})

@csrf_exempt
def check_balance(request):
    public_key = request.POST.get('public_key')
    print(public_key)
    server = Server("https://horizon-testnet.stellar.org")
    account = server.accounts().account_id(public_key).call()
    return JsonResponse({'balance': account['balances'][0]['balance']})



@csrf_exempt
def send_money(request):
    if request.method == 'POST':
        destination_public_key = request.POST.get('destination_public_key')
        amount = request.POST.get('amount')
        encryption_key = request.POST.get('encryption_key')
        wallet = Wallet.objects.filter(user=User.objects.first())[1]
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
        print(response)
        return JsonResponse({'message': 'Payment sent successfully'})
    else:
        pass
