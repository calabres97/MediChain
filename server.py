import node
import time
import json
import requests

from flask import Flask, request

app = Flask(__name__)

blockchain_ = node.Chain()
blockchain_.first_block()

peers_ = set()


def consensus():
    global blockchain_
    longest_chain = None
    current_len = len(blockchain_.chain_)

    for node_ in peers_:
        response = requests.get("{}chain".format(node_))
        length_ = response.json()["length_"]
        chain_ = response.json()["chain_"]
        if length_ > current_len and blockchain_.check_validity(chain_):
            current_len = length_
            longest_chain = chain_
    if longest_chain:
        blockchain_ = longest_chain
        return True
    return False


def create_from_dump(chain_):
    new_blockchain = node.Chain()
    for index, block_data in enumerate(chain_):
        block_ = node.Block(block_data["index_"],
                            block_data["transactions_"],
                            block_data["timestamp_"],
                            block_data["previous_hash"])
        pow_ = block_data["hash_"]
        if index > 0:
            added = new_blockchain.insert_block(block_, pow_)
            if not added:
                raise Exception("The chain dump is wrong")
        else:
            new_blockchain.chain_.append(block_)
    return new_blockchain


def announce_new_block(block_):
    headers = {
        'Content-Type': "application/json"
    }
    for peer_ in peers_:
        url = "{}block".format(peer_)
        print(requests.post(url,
                            data=json.dumps(block_.__dict__, sort_keys=True),
                            headers=headers))


@app.route('/transaction', methods=['POST'])
def transaction():
    transaction_data = request.get_json()
    fields = ["doctor",
              "patient",
              "illness",
              "description",
              "timestamp"]
    for field in fields:
        if not transaction_data.get(field):
            return "Invalid transaction data", 404

    transaction_data["timestamp"] = time.time()
    blockchain_.insert_new_transaction(transaction_data)
    return "Success", 200


@app.route('/chain', methods=['GET'])
def chain():
    consensus()
    chain_ = []
    for block_ in blockchain_.chain_:
        chain_.append(block_.__dict__)

    return json.dumps({"length_": len(chain_),
                       "chain_": chain_,
                       "peers_": list(peers_)})


@app.route('/transactions', methods=['GET'])
def transactions():
    patient_ = request.args.get('patient', default=None)
    consensus()
    transactions_ = []
    for block_ in blockchain_.chain_:
        if patient_ is not None:
            for tx_ in block_.transactions_:
                if patient_ == tx_['patient']:
                    transactions_.append(tx_)

    return json.dumps({"length_": len(transactions_),
                       "transactions_": transactions_,
                       "peers_": list(peers_)})


@app.route('/patients', methods=['GET'])
def patients():
    patients_ = []
    for block_ in blockchain_.chain_:
        for tx_ in block_.transactions_:
            if tx_['patient'] not in patients_:
                patients_.append(tx_['patient'])
    return json.dumps(patients_)


@app.route('/peers', methods=['GET'])
def get_peers():
    peers_connected = []
    if len(peers_) > 0:
        peers_connected = [list(peers_)]
    if request.host_url not in peers_connected:
        peers_connected.append(request.host_url)
    return json.dumps(peers_connected)


@app.route('/mine', methods=['GET'])
def mine_transactions_remaining():
    block_ = blockchain_.mine()
    if not block_:
        return "No transactions remaining to mine"
    announce_new_block(block_)
    return "Mined block number {} correctly".format(block_.index_)


@app.route('/new_peer', methods=['POST'])
def add_new_peer():
    node_ip = request.get_json()["node_ip"]
    if not node_ip:
        return "Invalid data", 400

    peers_.add(node_ip)
    print("Peeeeeers " + request.host_url)
    print(peers_)
    return chain()


@app.route('/add_with_existing_peer', methods=['POST'])
def add_with_existing_peer():
    node_ip = request.get_json()["node_ip"]
    if not node_ip:
        return "Invalid data", 400

    data = {
        "node_ip": request.host_url
    }
    headers = {
        'Content-Type': "application/json"
    }

    response = requests.post(node_ip + "/new_peer",
                             data=json.dumps(data),
                             headers=headers)

    if response.status_code == 200:
        global blockchain_
        global peers_
        chain_dump = response.json()["chain_"]
        blockchain_ = create_from_dump(chain_dump)
        peers_.add(request.url_root)
        for peer_ in response.json()['peers_']:
            if peer_ != request.host_url:
                peers_.add(peer_)
        print("Peeeeeers " + request.host_url)
        print(peers_)
        return "Registration succesfull", 200
    else:
        return response.content, response.status_code


@app.route('/block', methods=['POST'])
def verify_block():
    block_data = request.get_json()
    block_ = node.Block(block_data["index_"],
                        block_data["transactions_"],
                        block_data["timestamp_"],
                        block_data["previous_hash"])

    pow_ = block_data["hash_"]
    added = blockchain_.insert_block(block_, pow_)
    if not added:
        return "The block was discarded and not added by the node", 400
    return "Block added to the chain", 200


@app.route('/remaining_transactions', methods=['GET'])
def remaining_transactions():
    return json.dumps(blockchain_.transactions_remaining)
