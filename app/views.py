import datetime
import requests
import time

from flask import render_template, redirect, request, url_for

from app import app

history = []
chain = []


def fetch_history(patient_):
    """
    Fetch all hisory for one patient from the blockchain and store it locally
    """
    get_chain_address = "{}/transactions".format(get_client_ip())
    if patient_ is not None:
        get_chain_address += "?patient={}".format(patient_)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        global history
        history = sorted(response.json()['transactions_'], key=lambda k: k['timestamp'], reverse=True)


def fetch_chain():
    """
    Fetch all the blockchain and store it locally
    """
    get_chain_address = "{}/chain".format(get_client_ip())
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain_content = response.json()
        for block in chain_content["chain_"]:
            for transaction in block["transactions_"]:
                transaction["index_"] = block["index_"]
                transaction["hash_"] = block["previous_hash"]
                content.append(transaction)
        global chain
        chain = sorted(content, key=lambda k: k['timestamp'], reverse=False)


def fetch_patients():
    get_patients_address = "{}/patients".format(get_client_ip())
    response = requests.get(get_patients_address)
    if response.status_code == 200:
        global patients
        patients = response.json()


@app.route('/')
def index():
    fetch_patients()
    return render_template('index.html',
                           title="MediChain",
                           patients=patients,
                           node_address=get_client_ip())


@app.route('/history', methods=['GET', 'POST'])
def history():
    patient_ = request.args.get('patient')
    if patient_ is None:
        if 'patient' in request.form.keys():
            patient_ = request.form['patient']
        else:
            return redirect(url_for('index'))

    patient_ = "{}".format(patient_)
    print(patient_)

    fetch_history(patient_)
    return render_template('history.html',
                           title="MediChain",
                           history=history,
                           patient=patient_,
                           node_address=get_client_ip(),
                           readable_time=timestamp_to_string)


@app.route('/chain', methods=['GET'])
def chain():
    fetch_chain()
    return render_template('chain.html',
                           title="MediChain",
                           chain=chain,
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

    obj = {
        'author': author,
        'patient': patient,
        'illness': illness,
        'description': description,
        'timestamp': time.time()
    }

    new_transaction_address = "{}/transaction".format(get_client_ip())
    requests.post(new_transaction_address,
                  json=obj,
                  headers={'Content-Type': 'application/json'})
    return redirect(url_for('history') + "?patient=" + patient)


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


def get_client_ip():
    return "http://" + request.remote_addr + ":8000"
