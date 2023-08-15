function loadData() {
  fetch("./json/cchbalance.json")
    .then(response => response.json())
    .then(data => processData(data));
}

function processData(data) {
  const companyNameElement = document.getElementById("company_name");
  const accountingMethodElement = document.getElementById("accounting_method");
  const asOfDateElement = document.getElementById("as_of_date");
  const statement = document.getElementById("statement");

  companyNameElement.innerText = data.company_name;
  accountingMethodElement.innerText = data.accounting_method;
  asOfDateElement.innerHTML = `As of ${data.as_of_date}`;

  const addCategoryRows = (category, items) => {
    let total = 0;
    items.forEach(item => {
      if (item.category === category) {
        total += item.amount;
        statement.insertAdjacentHTML("beforeend", `<tr class="item-row"><td>${item.description}</td><td class="text-end">${item.amount.toLocaleString()}</td></tr>`);
      }
    });
    return total;
  };

  // Assets
  statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Assets</th></tr>`);
  let totalCurrentAssets = addCategoryRows("Current Assets", data.assets);
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Current Assets</th><td class="text-end">${totalCurrentAssets.toLocaleString()}</td></tr>`);

  let totalFixedAssets = addCategoryRows("Fixed Assets", data.assets);
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Fixed Assets</th><td class="text-end">${totalFixedAssets.toLocaleString()}</td></tr>`);

  let totalAssets = totalCurrentAssets + totalFixedAssets;
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="sub_main_header">Total Assets</th><td class="text-end">${totalAssets.toLocaleString()}</td></tr>`);

  statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);

    // Liabilities
  statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Liabilities</th></tr>`);
  let totalCurrentLiabilities = addCategoryRows("Current Liabilities", data.liabilities);
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Current Liabilities</th><td class="text-end">${totalCurrentLiabilities.toLocaleString()}</td></tr>`);

  let totalLongTermLiabilities = addCategoryRows("Long-Term Liabilities", data.liabilities);
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Long-Term Liabilities</th><td class="text-end">${totalLongTermLiabilities.toLocaleString()}</td></tr>`);

  let totalLiabilities = totalCurrentLiabilities + totalLongTermLiabilities;
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="sub_main_header">Total Liabilities</th><td class="text-end">${totalLiabilities.toLocaleString()}</td></tr>`);

  statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);

  // Owner's Equity
  statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Owner's Equity</th></tr>`);
  let totalEquity = addCategoryRows("Owner's Equity", data.equity);
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Owner's Equity</th><td class="text-end">${totalEquity.toLocaleString()}</td></tr>`);

  statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);

  // Total Liabilities and Owner's Equity
  let totalLiabilitiesAndEquity = totalLiabilities + totalEquity;
  statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="sub_main_header">Total Liabilities & Owner's Equity</th><td class="text-end">${totalLiabilitiesAndEquity.toLocaleString()}</td></tr>`);
}

// Call the loadData function to fetch data from the JSON file and process it.
loadData();

