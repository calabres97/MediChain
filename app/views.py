import datetime
import requests
import time

from flask import render_template, redirect, request, url_for

from app import app

history = []
chain = []
peers = []
ip = None


def fetch_history(patient_):
    get_chain_address = "{}/transactions".format(ip)
    if patient_ is not None:
        get_chain_address += "?patient={}".format(patient_)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        global history
        history = sorted(response.json()['transactions_'], key=lambda k: k['timestamp'], reverse=True)


def fetch_chain():
    get_chain_address = "{}/chain".format(ip)
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
    get_patients_address = "{}/patients".format(ip)
    response = requests.get(get_patients_address)
    if response.status_code == 200:
        return response.json()


def fetch_peers():
    get_peers_address = "{}/peers".format(ip)
    response = requests.get(get_peers_address)
    if response.status_code == 200:
        global peers
        peers = response.json()


@app.route('/')
def index():
    patients = []
    if ip:
        patients = fetch_patients()
    return render_template('index.html',
                           title="MediChain",
                           patients=patients,
                           node_address=get_node_ip(),
                           is_empty=is_empty,
                           exists=exists,
                           ip=ip)


@app.route('/history', methods=['GET', 'POST'])
def history():
    new_ = request.args.get('new', default=None)
    patient_ = request.args.get('patient')
    if new_ is not None:
        global history
        history = []
    else:
        if patient_ is None:
            if 'patient' in request.form.keys():
                patient_ = request.form['patient']
            else:
                return redirect(url_for('index'))

        patient_ = "{}".format(patient_)
        fetch_history(patient_)

    return render_template('history.html',
                           title="MediChain",
                           history=history,
                           patient=patient_,
                           node_address=get_node_ip(),
                           readable_time=timestamp_to_string,
                           exists=exists)


@app.route('/chain', methods=['GET'])
def chain():
    fetch_chain()
    return render_template('chain.html',
                           title="MediChain",
                           chain=chain,
                           node_address=get_node_ip(),
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_new_history():
    description = request.form["description"]
    doctor = request.form["doctor"]
    patient = request.form["patient"]
    illness = request.form["illness"]

    obj = {
        'doctor': doctor,
        'patient': patient,
        'illness': illness,
        'description': description,
        'timestamp': time.time()
    }

    new_transaction_address = "{}/transaction".format(ip)
    response = requests.post(new_transaction_address,
                  json=obj,
                  headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        return redirect(url_for('history') + "?patient=" + patient)
    else:
        return redirect(url_for('index'))


@app.route('/new_peer', methods=['POST'])
def new_peer():
    ip_address = request.form['peer']

    obj = {
        'node_ip': ip
    }

    new_peer_address = "{}/add_with_existing_peer".format(ip_address)
    requests.post(new_peer_address,
                  json=obj,
                  headers={'Content-Type': 'application/json'})
    return redirect(url_for('peers'))


@app.route("/set_peer", methods=['POST'])
def set_peer():
    global ip
    ip = request.form["peer"]
    return redirect(url_for('index'))


@app.route('/peers')
def peers():
    fetch_peers()
    return render_template('peers.html',
                           title="MediChain | Peers",
                           peers=peers,
                           node_address=get_node_ip,
                           is_empty=is_empty)


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


def get_node_ip():
    url_ = request.host_url.split(":")
    final_url = url_[1][2:]
    return "http://" + final_url + ":8000"


def is_empty(obj):
    if not obj:
        return True
    return False


def exists(obj):
    if obj is None:
        return False
    return True
