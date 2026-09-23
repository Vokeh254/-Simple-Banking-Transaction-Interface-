# Simple Banking Transaction Interface

This project is a small Python + Flask banking dashboard that lets you:

- Create a bank account
- Deposit funds into an account
- Withdraw funds from an account
- Transfer money between accounts
- Delete a dormant account
- Create a loan account for a customer and disburse a KES 10,000 loan

## Features

- Frontend built with HTML, CSS, and JavaScript
- Python backend using Flask
- In-memory account storage for quick testing
- Dynamic account table that updates automatically after each transaction

## Run locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open the browser at:
   ```text
   http://localhost:5000
   ```

## Notes

- Account numbers are generated automatically.
- A dormant account is treated as inactive for more than 30 days.
- The delete dormant account flow accepts an inactive-day value so you can simulate dormancy in the UI.
- The loan feature creates a loan account and deposits the default KES 10,000 into the selected customer’s bank account.
