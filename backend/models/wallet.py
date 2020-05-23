from flask import jsonify, request
from databases import auth, wallet
from eth_account import Account
from web3 import Web3
import json

###########
# WARNING #
# MAINNET #
###########
###########
# WARNING #
# MAINNET #
###########


class Token:
    address = None
    name = None
    symbol = None
    decimals = None
    total_supply = None
    ABI = None


class Wallet(object):
    def __init__(self, checksum_address=Web3.toChecksumAddress("Address")):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Address"))
        self.token = Token()
        self.token.address = checksum_address
        with open("./models/ABI.json", "r") as data:
            self.token.ABI = json.load(data)
        self.contract = self.w3.eth.contract(self.token.address, abi=self.token.ABI)
        self.token.name = self.contract.functions.name().call()
        self.token.symbol = self.contract.functions.symbol().call()
        self.token.decimals = self.contract.functions.decimals().call()
        self.token.total_supply = self.contract.functions.totalSupply().call()

    @staticmethod
    def new(email):
        new_account = Account.create('KW' + email)
        wallet.Wallet(
            email=email,
            address=new_account.address,
            private_key=str(new_account.privateKey)
        ).save()
        user_object = auth.User.objects(email=email).first()
        user_object.wallet = new_account.address
        user_object.save()

        return jsonify({
            "success": True,
            "msg": "successful created new wallet",
            "wallet": new_account.address
        }), 200

    def balance(self, email):
        wallet_object = wallet.Wallet.objects(email=email).first()
        try:
            atcg_balance = "{}.{}".format(
                str(int(self.contract.functions.balanceOf(wallet_object.address).call() / (10 ** self.token.decimals))),
                str(int(self.contract.functions.balanceOf(wallet_object.address).call() % (10 ** self.token.decimals))))
        except Exception as e:
            print(e)
            atcg_balance = "0.0"
        # print(atcg_balance)
        try:
            eth_balance = "{}.{}".format(
                int(self.w3.eth.getBalance(wallet_object.address) / (10 ** (self.token.decimals+1))),
                int(self.w3.eth.getBalance(wallet_object.address) % (10 ** (self.token.decimals+1))))
        except Exception as e:
            print(e)
            eth_balance = "0.0"
        # print(eth_balance)

        return jsonify({
            "success": True,
            "eth": eth_balance,
            "atcg": atcg_balance
        }), 200

class ATCG(object):
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Address"))
        self.token = Token()
        self.token.address = "token.address"
        with open("./models/ABI.json", "r") as data:
            self.token.ABI = json.load(data)
        self.contract = self.w3.eth.contract(self.token.address, abi=self.token.ABI)
        self.token.name = self.contract.functions.name().call()
        self.token.symbol = self.contract.functions.symbol().call()
        self.token.decimals = self.contract.functions.decimals().call()
        self.token.total_supply = self.contract.functions.totalSupply().call()

    def transfer(self, email):
        my_wallet = wallet.Wallet.objects(email=email).first()
        to = request.form['to']
        amount = request.form['amount']

        atcg_balance = float("{}.{}".format(
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() / (10 ** self.token.decimals))),
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() % (10 ** self.token.decimals)))))
        if atcg_balance * 0.3 >= float(amount):
            contract_txn = self.contract.functions.transfer(
                to, int(amount) * (10 ** int(self.token.decimals)),
            ).buildTransaction({
                'chainId': 3,
                'gas': 100000,
                'gasPrice': self.w3.toWei('9.6', 'gwei'),
                'nonce': self.w3.eth.getTransactionCount(my_wallet.address),
                'from': my_wallet.address,
            })
            signed_txn = self.w3.eth.account.signTransaction(contract_txn, private_key=eval(my_wallet.private_key))
            tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            #print('send')
            #self.w3.eth.waitForTransactionReceipt(tx_hash)
            #print(self.w3.toHex(self.w3.sha3(tx_hash)))

            return jsonify({
                "success": True,
                "msg": "Transfer pending successfully!"
            }), 200
        else:
            return jsonify({
                "success": True,
                "msg": "Not enough ATCG!!"
            }), 200


class ETH(object):
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/Address"))
        self.token = Token()
        self.token.address = "token.address"
        with open("./models/ABI.json", "r") as data:
            self.token.ABI = json.load(data)
        self.contract = self.w3.eth.contract(Web3.toChecksumAddress(self.token.address), abi=self.token.ABI)
        self.token.name = self.contract.functions.name().call()
        self.token.symbol = self.contract.functions.symbol().call()
        self.token.decimals = self.contract.functions.decimals().call()
        self.token.total_supply = self.contract.functions.totalSupply().call()

    def transfer(self, email):
        my_wallet = wallet.Wallet.objects(email=email).first()
        to = request.form['to']
        amount = request.form['amount']

        try:
            signed_txn = self.w3.eth.account.signTransaction(dict(
                nonce=self.w3.eth.getTransactionCount(my_wallet.address),
                gasPrice=self.w3.eth.gasPrice,
                gas=100000,
                to=to,
                value=Web3.toWei(amount, 'ether')
            ),
                eval(my_wallet.private_key))

            self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

            return jsonify({
                "success": True,
                "msg": "ETH pending Successfully!!",
            }), 200
        except ValueError:
            return jsonify({
                "success": False,
                "msg": "Not enough ETH!!",
            }), 200

    def balance(self, email):
        my_wallet = wallet.Wallet.objects(email=email).first()

        eth_balance = float("{}.{}".format(
            str(int(self.w3.eth.getBalance(my_wallet.address) / (10 ** (self.token.decimals+1)))),
            str(int(self.w3.eth.getBalance(my_wallet.address) % (10 ** (self.token.decimals+1))))))

        return eth_balance


class ATCG_func(object):
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/address"))
        self.token = Token()
        self.token.address = "address"
        with open("./models/ABI.json", "r") as data:
            self.token.ABI = json.load(data)
        self.contract = self.w3.eth.contract(Web3.toChecksumAddress(self.token.address), abi=self.token.ABI)
        self.token.name = self.contract.functions.name().call()
        self.token.symbol = self.contract.functions.symbol().call()
        self.token.decimals = self.contract.functions.decimals().call()
        self.token.total_supply = self.contract.functions.totalSupply().call()

    def balance(self, email):
        my_wallet = wallet.Wallet.objects(email=email).first()

        atcg_balance = float("{}.{}".format(
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() / (10 ** self.token.decimals))),
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() % (10 ** self.token.decimals)))))

        return atcg_balance

    def transfer(self, email, to, amount):
        my_wallet = wallet.Wallet.objects(email=email).first()
        # to = request.form['to']
        # amount = request.form['amount']

        atcg_balance = float("{}.{}".format(
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() / (10 ** self.token.decimals))),
            str(int(self.contract.functions.balanceOf(my_wallet.address).call() % (10 ** self.token.decimals)))))
        if atcg_balance * 0.3 >= float(amount):
            contract_txn = self.contract.functions.transfer(
                to, int(amount) * (10 ** int(self.token.decimals)),
            ).buildTransaction({
                'chainId': 3,
                'gas': 100000,
                'gasPrice': self.w3.toWei('9.6', 'gwei'),
                'nonce': self.w3.eth.getTransactionCount(my_wallet.address),
                'from': my_wallet.address,
            })
            signed_txn = self.w3.eth.account.signTransaction(contract_txn, private_key=eval(my_wallet.private_key))
            tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            #self.w3.eth.waitForTransactionReceipt(tx_hash)
            #print(self.w3.toHex(self.w3.sha3(tx_hash)))

            return jsonify({
                "success": True,
                "msg": "Transfer pending successfully!"
            }), 200
        else:
            return jsonify({
                "success": True,
                "msg": "Not enough ATCG!!"
            }), 200
