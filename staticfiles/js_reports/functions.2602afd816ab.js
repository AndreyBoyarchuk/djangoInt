// Print function
function printContainer() {
  const buttonsContainer = document.querySelector('.buttons-container');
  if (buttonsContainer) { // Check if buttonsContainer is not null
    buttonsContainer.style.display = 'none';
    window.print();
    buttonsContainer.style.display = 'block';
  } else {
    console.error('Buttons container not found');
  }
}

// Attach the functions to the buttons
document.querySelector('button[onclick="printContainer()"]').onclick = printContainer;

