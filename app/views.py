import datetime
import requests

from flask import render_template, redirect, request

from app import app

history = []


def fetch_history():
    """
    Fetch all hisory from the blockchain and store it locally
    """
    get_chain_address = "{}/chain".format(get_client_ip())
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = response.json()
        for block in chain["chain_"]:
            for transaction in block["transactions_"]:
                transaction["index_"] = block["index_"]
                transaction["hash_"] = block["previous_hash"]
                content.append(transaction)

        global history
        history = sorted(content, key=lambda k: k['timestamp'], reverse=True)


@app.route('/')
def index():
    fetch_history()
    return render_template('index.html',
                           title="MediChain",
                           history=history,
                           node_address=get_client_ip(),
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_new_history():
    """
    Create a new transaction on the chain
    """
    description = request.form["description"]
    author = request.form["author"]
    patient = request.form["patient"]
    illness = request.form["illness"]

    object = {
        'author': author,
        'patient': patient,
        'illness': illness,
        'description': description,
    }

    new_transaction_address = "{}/transaction".format(get_client_ip())
    requests.post(new_transaction_address,
                  json=object,
                  headers={'Content-Type': 'application/json'})
    return redirect("/")


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


def get_client_ip():
    return "http://" + request.remote_addr + ":8000"
