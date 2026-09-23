const showMessage = (text, type = 'success') => {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message visible ${type}`;
};

const formatMoney = (value) => {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
};

const renderAccounts = (accounts) => {
  const tbody = document.getElementById('accounts-table-body');
  tbody.innerHTML = '';

  if (!accounts.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6">No accounts found.</td>
      </tr>
    `;
    return;
  }

  accounts.forEach((account) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${account.holder_name}</td>
      <td>${account.account_number}</td>
      <td>${formatMoney(account.balance)}</td>
      <td>
        <span class="status-pill ${account.is_dormant ? 'dormant' : 'active'}">
          ${account.is_dormant ? 'Dormant' : 'Active'}
        </span>
      </td>
      <td>${account.loan_account_number || 'N/A'}</td>
      <td>${account.loan_account_number ? formatMoney(account.loan_balance) : 'KES 0.00'}</td>
    `;
    tbody.appendChild(row);
  });
};

const getAccounts = async () => {
  const response = await fetch('/api/accounts');
  const data = await response.json();
  renderAccounts(data.accounts || []);
};

const handleSubmit = async (formId, endpoint, successMessage) => {
  const form = document.getElementById(formId);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) {
      showMessage(result.message || 'Something went wrong.', 'error');
      return;
    }

    showMessage(result.message || successMessage, 'success');
    form.reset();
    await getAccounts();
  });
};

const initialize = () => {
  handleSubmit('create-account-form', '/api/accounts', 'Account created successfully.');
  handleSubmit('deposit-form', '/api/deposit', 'Deposit successful.');
  handleSubmit('withdraw-form', '/api/withdraw', 'Withdrawal successful.');
  handleSubmit('transfer-form', '/api/transfer', 'Transfer completed.');
  handleSubmit('delete-dormant-form', '/api/delete-dormant', 'Dormant account deleted successfully.');
  handleSubmit('loan-form', '/api/loan', 'Loan disbursed successfully.');

  document.getElementById('refresh-accounts').addEventListener('click', getAccounts);
  getAccounts();
};

initialize();
