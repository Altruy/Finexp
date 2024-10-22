import json
import os
import uuid

DB_FILE = 'local_database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def save_transaction(who, transaction):
    db = load_db()
    if who not in db:
        db[who] = []
    transaction_id = str(uuid.uuid4())
    transaction['id'] = transaction_id
    db[who].append(transaction)
    save_db(db)
    return transaction

def reset_transaction(who, transactions):
    db = load_db()
    db[who] = []
    for transaction in transactions:
        db[who].append(transaction)
    save_db(db)
    return True

def get_transactions(who):
    db = load_db()
    print(who)
    print(db)
    return db.get(who, [])

def update_transaction(who, transaction_id, updated_transaction):
    db = load_db()
    if who in db:
        for i, transaction in enumerate(db[who]):
            if transaction['id'] == transaction_id:
                db[who][i] = {**transaction, **updated_transaction, 'id': transaction_id}
                save_db(db)
                return db[who][i]
    return None

def delete_transaction(who, transaction_id):
    db = load_db()
    if who in db:
        db[who] = [transaction for transaction in db[who] if transaction['id'] != transaction_id]
        save_db(db)
        return True
    return False
