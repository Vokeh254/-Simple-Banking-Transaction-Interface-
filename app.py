from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

accounts = []


def generate_account_number():
    return f"ACC-{uuid.uuid4().hex[:8].upper()}"


def generate_loan_account_number():
    return f"LOAN-{uuid.uuid4().hex[:8].upper()}"


def get_account(identifier):
    for account in accounts:
        if str(account["id"]) == str(identifier):
            return account
        if account["account_number"] == str(identifier):
            return account
    return None


def account_snapshot(account):
    last_activity = account["last_activity"]
    dormant_days = (datetime.utcnow() - last_activity).days
    is_dormant = dormant_days >= 30
    return {
        "id": account["id"],
        "account_number": account["account_number"],
        "holder_name": account["holder_name"],
        "balance": account["balance"],
        "created_at": account["created_at"],
        "last_activity": account["last_activity"],
        "dormant_days": dormant_days,
        "is_dormant": is_dormant,
        "loan_account_number": account.get("loan_account_number"),
        "loan_balance": account.get("loan_balance", 0),
        "loan_disbursed_at": account.get("loan_disbursed_at"),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/accounts", methods=["GET"])
def list_accounts():
    return jsonify({"accounts": [account_snapshot(account) for account in accounts]})


@app.route("/api/accounts", methods=["POST"])
def create_account():
    payload = request.get_json(silent=True) or {}
    holder_name = (payload.get("holder_name") or "").strip()
    initial_deposit = float(payload.get("initial_deposit", 0) or 0)

    if not holder_name:
        return jsonify({"message": "Account holder name is required."}), 400
    if initial_deposit < 0:
        return jsonify({"message": "Initial deposit cannot be negative."}), 400

    account = {
        "id": str(uuid.uuid4()),
        "account_number": generate_account_number(),
        "holder_name": holder_name,
        "balance": initial_deposit,
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_activity": datetime.utcnow(),
        "loan_account_number": None,
        "loan_balance": 0,
        "loan_disbursed_at": None,
    }
    accounts.append(account)
    return jsonify({"message": "Bank account created successfully.", "account": account_snapshot(account)}), 201


@app.route("/api/deposit", methods=["POST"])
def deposit_funds():
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0) or 0)

    if amount <= 0:
        return jsonify({"message": "Deposit amount must be greater than zero."}), 400

    account = get_account(account_id)
    if not account:
        return jsonify({"message": "Account not found."}), 404

    account["balance"] += amount
    account["last_activity"] = datetime.utcnow()
    return jsonify({"message": "Deposit successful.", "account": account_snapshot(account)})


@app.route("/api/withdraw", methods=["POST"])
def withdraw_funds():
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0) or 0)

    if amount <= 0:
        return jsonify({"message": "Withdrawal amount must be greater than zero."}), 400

    account = get_account(account_id)
    if not account:
        return jsonify({"message": "Account not found."}), 404
    if account["balance"] < amount:
        return jsonify({"message": "Insufficient account balance."}), 400

    account["balance"] -= amount
    account["last_activity"] = datetime.utcnow()
    return jsonify({"message": "Withdrawal successful.", "account": account_snapshot(account)})


@app.route("/api/transfer", methods=["POST"])
def transfer_funds():
    payload = request.get_json(silent=True) or {}
    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = float(payload.get("amount", 0) or 0)

    if amount <= 0:
        return jsonify({"message": "Transfer amount must be greater than zero."}), 400
    if from_account_id == to_account_id:
        return jsonify({"message": "Source and destination accounts must be different."}), 400

    source = get_account(from_account_id)
    target = get_account(to_account_id)
    if not source:
        return jsonify({"message": "Source account not found."}), 404
    if not target:
        return jsonify({"message": "Destination account not found."}), 404
    if source["balance"] < amount:
        return jsonify({"message": "Insufficient funds for transfer."}), 400

    source["balance"] -= amount
    target["balance"] += amount
    source["last_activity"] = datetime.utcnow()
    target["last_activity"] = datetime.utcnow()
    return jsonify({
        "message": "Funds transferred successfully.",
        "source": account_snapshot(source),
        "target": account_snapshot(target),
    })


@app.route("/api/delete-dormant", methods=["POST"])
def delete_dormant_account():
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("account_id")
    inactive_days = int(payload.get("inactive_days", 45) or 45)

    account = get_account(account_id)
    if not account:
        return jsonify({"message": "Account not found."}), 404

    account["last_activity"] = datetime.utcnow() - timedelta(days=inactive_days)
    if (datetime.utcnow() - account["last_activity"]).days < 30:
        return jsonify({"message": "This account is not yet dormant. At least 30 days of inactivity is required."}), 400

    accounts[:] = [item for item in accounts if item["id"] != account["id"]]
    return jsonify({"message": "Dormant account deleted successfully.", "deleted_account": account_snapshot(account)})


@app.route("/api/loan", methods=["POST"])
def create_loan_account():
    payload = request.get_json(silent=True) or {}
    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 10000) or 10000)

    account = get_account(account_id)
    if not account:
        return jsonify({"message": "Account not found."}), 404
    if amount <= 0:
        return jsonify({"message": "Loan amount must be greater than zero."}), 400

    if account.get("loan_account_number"):
        return jsonify({"message": "A loan account already exists for this customer.", "account": account_snapshot(account)}), 400

    loan_account_number = generate_loan_account_number()
    account["loan_account_number"] = loan_account_number
    account["loan_balance"] = amount
    account["loan_disbursed_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    account["balance"] += amount
    account["last_activity"] = datetime.utcnow()

    return jsonify({
        "message": "Loan account created and funds disbursed successfully.",
        "loan_account_number": loan_account_number,
        "loan_amount": amount,
        "account": account_snapshot(account),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
