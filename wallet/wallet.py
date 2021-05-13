# import libraries
import subprocess
import json
import os
from dotenv import load_dotenv
from constants import *
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

load_dotenv()

# import mnemonic from env
mnemonic = os.getenv("mnemonic")

# connect to local ETH/ geth
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

 
# create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f'php derive -g --mnemonic="{mnemonic}" --coin="{coin}" --numderive="{numderive}" --format=json'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"eth", "btc-test", "btc"}
numderive = 3

keys = {}
for coin in coins:
    keys[coin]= derive_wallets(mnemonic, coin, numderive=3)

print(json.dumps(keys, indent=4, sort_keys=True))

eth_PrivateKey = keys["eth"][0]['privkey']
btc_PrivateKey = keys['btc-test'][0]['privkey']

print(eth_PrivateKey)
print(btc_PrivateKey)

# create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin,priv_key):
    print(coin)
    print(priv_key)
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

# create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from":eth_acc.address, "to":recipient, "value": amount}
        )
        return { 
            "from": eth_acc.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_acc.address)
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

# create a function to hold Ethereum 
eth_acc = priv_key_to_account(ETH, derive_wallets(mnemonic, ETH,5)[0]['privkey'])

# create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_txn(coin,account,recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        tx_btctest = create_tx(coin, account, recipient, amount)
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)

# BTC-TEST Transactions
btc_acc = priv_key_to_account(BTCTEST,btc_PrivateKey)

create_tx(BTCTEST,btc_acc,"mtwKEtSHmt9xuBSFLeWNXWQDPKTEK1rhtV", 0.001)

# send BTC transaction
send_txn(BTCTEST,btc_acc,"mg5XJJKR4jgf5PTMkRDBJZzn6hfyVfyHzS", 0.001)

# ETH Transactions

