
const dataUrl = "profitAndLossData";

fetch(dataUrl)
    .then(response => response.json())
    .then(data => {
        processData(data);
    })
    .catch(error => {
        console.error("Error loading data:", error);
    });


function processData(data) {
    const companyNameElement = document.getElementById("company_name");
    const accountingMethodElement = document.getElementById("accounting_method");
    const periodElement = document.getElementById("period");
    const printDateElement = document.getElementById("print_date");
    const statement = document.getElementById("statement");

    let totalIncome = 0;
    let totalExpenses = 0;
    let totalCOGS = 0;
    let totalOtherIncome = 0;
    let totalOtherExpenses = 0

    // Calculate total income and other income
    data.income.forEach(item => {
        if (item.category === "Operating Income") {
            totalIncome += item.amount;
        } else if (item.category === "Other Income") {
            totalOtherIncome += item.amount;
        }
    });

    // Calculate total expenses and COGS
    data.expenses.forEach(item => {
        if (item.category === "Operating Expenses") {
            totalExpenses += item.amount;
        } else if (item.category === "COGS") {
            totalCOGS += item.amount;
        }
    });

// Format total expenses and COGS with trailing zeros
    const formattedTotalExpenses = totalExpenses.toLocaleString(undefined, {minimumFractionDigits: 2});
    const formattedTotalCOGS = totalCOGS.toLocaleString(undefined, {minimumFractionDigits: 2});


    // Function to add category rows
    const addCategoryRows = (category, items) => {
        let total = 0;
        items
            .filter(item => item.category === category)
            .sort((a, b) => b.amount - a.amount) // sort items by amount in descending order
            .forEach(item => {
                total += item.amount;
                statement.insertAdjacentHTML("beforeend", `<tr class="item-row"><td>${item.description}</td><td class="text-end">${item.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
            });
        return total;
    };


    // Display company information
    companyNameElement.innerText = data.company_name;
    const currentDate = new Date();

// Display the date in the print_date element in MST timezone
    printDateElement.innerText = "Printed on: " +currentDate.toLocaleString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "America/Denver"
    });
    accountingMethodElement.innerText = data.accounting_method;


    periodElement.innerHTML = `For the Period ${data.start_date} to ${data.end_date}`;

    // Operating Income
    statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Income</th></tr>`);
    addCategoryRows("Operating Income", data.income);
    statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Income</th><td class="text-end">${totalIncome.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);

    statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);

    // COGS (if exists)
    if (totalCOGS > 0) {
        statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Cost of Goods Sold</th></tr>`);
        addCategoryRows("COGS", data.expenses);
        statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total COGS</th><td class="text-end">${totalCOGS.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
    }

    // Calculate gross profit
    const grossProfit = totalIncome - totalCOGS;

// Add row for gross profit to statement element
    statement.insertAdjacentHTML("beforeend", `<tr><th class="sub_main_header">Gross Profit</th><td class="text-end">${grossProfit.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);

// Add separator row to statement element
    statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);


    // Operating Expenses
    statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Operating Expenses</th></tr>`);
    addCategoryRows("Operating Expenses", data.expenses
    );
    statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Operating Expenses</th><td class="text-end">${totalExpenses.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);

    statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);


// Check if there's any "Other Income" or "Other Expenses" items
    const hasOtherIncome = data.income.some(item => item.category === "Other Income");
    const hasOtherExpenses = data.expenses.some(item => item.category === "Other Expenses");

// Ordinary Income
    if (hasOtherIncome || hasOtherExpenses) {
        const ordinaryIncome = totalIncome - totalExpenses - totalCOGS;
        statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Ordinary Income</th><td class="text-end">${ordinaryIncome.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
        statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);
    }

    // Other Income (if exists)
    if (totalOtherIncome > 0) {
        statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Other Income</th></tr>`);
        addCategoryRows("Other Income", data.income);
        statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Other Income</th><td class="text-end">${totalOtherIncome.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
    }

    statement.insertAdjacentHTML("beforeend", `<tr class="separator"><td colspan="2"></td></tr>`);

    // Other Expenses (if exists)

    data.expenses.forEach(item => {
        if (item.category === "Other Expenses") {
            totalOtherExpenses += item.amount;
        }
    });

    if (totalOtherExpenses > 0) {
        statement.insertAdjacentHTML("beforeend", `<tr><th colspan="2" class="main-header">Other Expenses</th></tr>`);
        addCategoryRows("Other Expenses", data.expenses);
        statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Total Other Expenses</th><td class="text-end">${totalOtherExpenses.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
    }

// Adjusted Net Profit/Loss
    const adjustedNetProfitLoss = totalOtherIncome - totalOtherExpenses
    if (adjustedNetProfitLoss !== 0) {
        statement.insertAdjacentHTML("beforeend", `<tr class="subtotal"><th class="total-header">Net Other Income/Loss</th><td class="text-end">${adjustedNetProfitLoss.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);
    }

    // Net Profit/Loss
    const netProfitLoss = grossProfit - totalExpenses + adjustedNetProfitLoss;
    statement.insertAdjacentHTML("beforeend", `<tr><th class="sub_main_header">Net Profit/Loss</th><td class="text-end">${netProfitLoss.toLocaleString(undefined, {minimumFractionDigits: 2})}</td></tr>`);

}

// Call the loadData function to fetch data from the JSON file and process it.
loadData();
