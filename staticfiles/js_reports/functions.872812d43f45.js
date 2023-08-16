// Print function
// Print function
function printContainer() {
  const buttonsContainer = document.querySelector('.buttons-container');
  buttonsContainer.style.display = 'none';
  window.print();

  buttonsContainer.style.display = 'block';
  // restore the previous display state of the preparer-info div

}


// Create PDF function
function createPDF() {
  // You can use a library like jsPDF to create the PDF
  // https://github.com/MrRio/jsPDF

  // Import the jsPDF library in your HTML file
  // <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.3.1/jspdf.umd.min.js"></script>

  const doc = new jsPDF();

  const container = document.querySelector('.container');
  doc.fromHTML(container, 15, 15, {
    'width': 170
  });

  doc.save('profit-and-loss-statement.pdf');
}

// Send Email function
function sendEmail() {
  // For this example, we'll use the email.js library to send the email
  // https://www.emailjs.com/docs/sdk/installation/

  // Import the email.js library in your HTML file
  // <script src="https://cdn.jsdelivr.net/npm/emailjs-com@2.3.2/dist/email.min.js"></script>

  // Initialize emailjs (replace YOUR_USER_ID with your actual email.js user ID)
  // emailjs.init('YOUR_USER_ID');

  const container = document.querySelector('.container');
  const emailContent = `
    <html>
      <head>
        <style>
          /* Your CSS styles here */
        </style>
      </head>
      <body>
        ${container.innerHTML}
      </body>
    </html>
  `;

  const templateParams = {
    to_email: 'recipient@example.com',
    subject: 'Profit and Loss Statement',
    html_message: emailContent
  };

  emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', templateParams)
    .then(() => {
      alert('Email sent!');
    }, (error) => {
      console.error('Failed to send email: ', error);
    });
}




// Attach the functions to the buttons
document.querySelector('button[onclick="printContainer()"]').onclick = printContainer;
document.querySelector('button[onclick="createPDF()"]').onclick = createPDF;
document.querySelector('button[onclick="sendEmail()"]').onclick = sendEmail;

