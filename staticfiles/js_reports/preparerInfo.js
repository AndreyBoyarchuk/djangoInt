function loadPreparerInfo() {
  fetch('./json/firmInfo.json')
    .then(response => {
      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }
      return response.json();
    })
    .then(json => {
      const preparerInfo = document.getElementById('preparer-info');
      preparerInfo.innerHTML = `
        <h2>Preparer Information</h2>
        <p> ${json.accountingFirm.name}</p>
        <p> ${json.accountingFirm.address.line1}</p>
        <p> ${json.accountingFirm.address.line2}</p>
        <p>Name: ${json.preparer.name}</p>
        <p>Email: ${json.preparer.email}</p>
        <p>PTIN: ${json.preparer.PTIN}</p>
        <p>Signature: ${json.preparer.signature}</p>
        <p>Date: ${json.preparer.date}</p>
      `;
    })
    .catch(function () {
      console.log("Error loading preparer information.");
    });
}

window.onload = loadPreparerInfo;
