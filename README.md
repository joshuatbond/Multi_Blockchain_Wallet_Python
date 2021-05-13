# Multi_Blockchain Wallet Python

## Background

A new startup is focused on building a portfolio management system that supports not only traditional assets like gold, silver, stocks, etc, but crypto-assets as well. The problem is, there are so many coins out there. As a result, we are tasked with understanding how HD wallets work, and building out a system that can create them.

In a effort to race to capture the market, we are going to use a command line tool, `hd-wallet-derive` that supports not only BIP32, BIP39, and BIP44, but also supports non-standard derivation paths for the most popular wallets available today. However, we will need to integrate the script into the backend with `python`. 

Once integration of this "universal" wallet is completed, we can begin to manage billions of addresses across 300+ coins, giving us a serious edge against the competition.

## Dependencies

- PHP must be installed on your operating system.
- You will need to clone the [`hd-wallet-derive`](https://github.com/dan-da/hd-wallet-derive) tool.
- [`bit`](https://ofek.github.io/bit/) Python Bitcoin library.
- [`web3.py`](https://github.com/ethereum/web3.py) Python Ethereum library.

## Step-by-step Guide

### 1. Project setup

* Create a project directory called `wallet` and `cd` into it.
* Clone the `hd-wallet-derive` tool into this folder and install it using the instructions on its `README.md`.
* Create a symlink called `derive` for the `hd-wallet-derive/hd-wallet-derive.php` script into the top level project directory like so: `ln -s hd-wallet-derive/hd-wallet-derive.php derive`. This will clean up the command needed to run the script in the code, to call `./derive` instead of `./hd-wallet-derive/hd-wallet-derive.php.exe`.
* Create a file called `wallet.py` -- universal wallet script.
* The directory tree for `hd-wallet-derive` should look like this:

![directory-tree](Images/tree.png)

### 2. Setup constants

* In a separate file, `constants.py`, set the following constants:
  * `BTC = 'btc'`
  * `ETH = 'eth'`
  * `BTCTEST = 'btc-test'`
* In `wallet.py`, import all constants: `from constants import *`
* Use these anytime to reference these strings, both in function calls, and in setting object keys.

### 3. Generate a Mnemonic

* Generate a new 12 word mnemonic using `hd-wallet-derive` or by using [this tool](https://iancoleman.io/bip39/).
* Set this mnemonic as an environment variable, and include the one generated as a fallback using: `mnemonic = os.getenv('MNEMONIC', 'insert mnemonic here')`

### 4. Deriving the wallet keys

* Use the `subprocess` library to call the `./derive` script from Python. Make sure to properly wait for the process.
* The following flags must be passed into the shell command as variables:
  * Mnemonic (`--mnemonic`) must be set from an environment variable, or default to a test mnemonic
  * Coin (`--coin`)
  * Numderive (`--numderive`) to set number of child keys generated
* Set the `--format=json` flag, then parse the output into a JSON object using `json.loads(output)`
* Wrap all of this into one function, called `derive_wallets`
* When done properly, the final object should look something like this (there are only 3 children each in this image):

![wallet_keys](Images/keys.png)

* You should now be able to select child accounts (and thus, private keys) by accessing items in the `coins` dictionary like so: `coins[COINTYPE][INDEX]['privkey']`.

### 5. Linking the transaction signing libraries

Use `bit` and `web3.py` to leverage the keys obtained in the `coins` object. Create 3 more funtions:

1. `priv_key_to_account` -- this will convert the `privkey` string in a child key to an account object that `bit` or `web3.py` can use to transact. This function needs the following parameters:

* `coin` -- the coin type (defined in `constants.py`).
* `priv_key` -- the `privkey` string will be passed through here.

Check the coin, then return one of the following functions based on the library:

* For `ETH`, return `Account.privateKeyToAccount(priv_key)`
* For `BTCTEST`, return `PrivateKeyTestnet(priv_key)`

2. `create_tx` -- this will create the raw, unsigned transaction that contains all metadata needed to transact. This function needs the following parameters:

* `coin` -- the coin type (defined in `constants.py`).
* `account` -- the account object from `priv_key_to_account`.
* `to` -- the recipient address.
* `amount` -- the amount of the coin to send.

Check the coin, then return one of the following functions based on the library:

* For `ETH`, return an object containing `to`, `from`, `value`, `gas`, `gasPrice`, `nonce`, and `chainID`. Make sure to calculate all of these values properly using `web3.py`!
* For `BTCTEST`, return `PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])`

3. `send_tx` -- this will call `create_tx`, sign the transaction, then send it to the designated network. This function needs the following parameters:

* `coin` -- the coin type (defined in `constants.py`).
* `account` -- the account object from `priv_key_to_account`.
* `to` -- the recipient address.
* `amount` -- the amount of the coin to send.

Check the coin, then create a `raw_tx` object by calling `create_tx`. Then, sign the `raw_tx` using `bit` or `web3.py` (hint: the account objects have a sign transaction function within).

Once signed the transaction, send it to the designated blockchain network.

* For `ETH`, return `w3.eth.sendRawTransaction(signed.rawTransaction)`
* For `BTCTEST`, return `NetworkAPI.broadcast_tx_testnet(signed)`

### 6. Sending transactions

- Now, you should be able to fund these wallets using testnet faucets.
- Open up a new terminal window inside of `wallet`.
- Then run the command `python` to open the Python shell.
- Within the Python shell, run the command `from wallet import *`. This will allow you to access the functions in `wallet.py` interactively.
- You'll need to set the account with  `priv_key_to_account` and use `send_tx` to send transactions.

**Bitcoin Testnet transaction**

`btc_acc = priv_key_to_account(BTCTEST,btc_PrivateKey)`

`create_tx(BTCTEST,btc_acc,"mtwKEtSHmt9xuBSFLeWNXWQDPKTEK1rhtV", 0.001)`

`send_txn(BTCTEST,btc_acc,"mg5XJJKR4jgf5PTMkRDBJZzn6hfyVfyHzS", 0.001)`

![btc_transaction](Images/btc_transaction.png)

**ETH transaction**

* Add one of the `ETH` addresses to the pre-allocated accounts in your `networkname.json`.
* Initialize using `geth --datadir nodeX init mtestnet.json`.
* [Add the following middleware](https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority) to `web3.py` to support the PoA algorithm:

```
from web3.middleware import geth_poa_middleware 
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
```

* Due to a bug in `web3.py`, you will need to send a transaction or two with MyCrypto first, since the
  `w3.eth.generateGasPrice()` function does not work with an empty chain. You can use one of the `ETH` address `privkey`, or one of the `node` keystore files.

* Send a transaction from the pre-funded address within the wallet to another, then get the `TxStatus` from MyCrypto
