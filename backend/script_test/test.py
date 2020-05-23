from eth_account import Account
from web3 import Web3
import json
from decimal import Decimal


class Token:
    ABI: str = None
    address: str = None
    name: str = None
    symbol: str = None
    decimals = None
    total_supply = None


class Wallet:
    address: str = None
    private_key = None
    balance = None


w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/address"))
new_account = Account.create("account")
token = Token()
with open("ABI.json", "r") as data:
    token.ABI = json.load(data)
token.address = "token.address"
contract = w3.eth.contract(token.address, abi=token.ABI)
token.name = contract.functions.name().call()
token.symbol = contract.functions.symbol().call()
token.decimals = contract.functions.decimals().call()
token.total_supply = contract.functions.totalSupply().call()

print(token.address,
      token.name,
      token.symbol,
      token.decimals,
      token.total_supply)

my_wallet = Wallet()
#my_wallet.address = new_account.address
my_wallet.address = "my_wallet.address"
my_wallet.balance = "{}.{}".format(int(contract.functions.balanceOf(my_wallet.address).call() / (10 ** token.decimals)),
                                   int(contract.functions.balanceOf(my_wallet.address).call() % (10 ** token.decimals)))
#my_wallet.private_key = new_account.privateKey
my_wallet.private_key = b'wallet.private_key'

print(my_wallet.address,
      my_wallet.balance)
print(w3.eth.getBalance(my_wallet.address))
nonce = w3.eth.getTransactionCount(my_wallet.address)
print(nonce, w3.toHex(w3.sha3(my_wallet.private_key)))
w3.eth.defaultAccount = my_wallet.address
print(w3.eth.defaultAccount)

signed_txn = w3.eth.account.signTransaction(dict(
    nonce=w3.eth.getTransactionCount(my_wallet.address),
    gasPrice=w3.eth.gasPrice,transaction = {
    'from': , # Only 'from' address, don't insert 'to' address
    'value': 0, # Add how many ethers you'll transfer during the deploy
    'gas': 2000000, # Trying to make it dynamic ..
    'gasPrice': self.w3.eth.gasPrice, # Get Gas Price
    'nonce': self.w3.eth.getTransactionCount(self.pub), # Get Nonce
    'data': tx_data # Here is the data sent through the network
}
# Sign the transaction using your private key
signed = self.w3.eth.account.signTransaction(transaction, self.priv)
#print(signed.rawTransaction)
tx_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
print(tx_hash.hex())
    gas=100000,
    to='to',
    value=w3.toWei(0.1, 'ether')
), my_wallet.private_key)
transactionHash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
print('send', transactionHash)
print(signed_txn)
