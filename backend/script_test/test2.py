from web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/address"))

try:
    signed_txn = w3.eth.account.signTransaction(dict(
        nonce=w3.eth.getTransactionCount('address'),
        gasPrice=w3.eth.gasPrice,
        gas=100000,
        to='to',
        value=Web3.toWei(0.1, 'ether')
      ),
      b'binary')

    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
except ValueError:
    print('a')
