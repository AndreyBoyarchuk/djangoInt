function activateNavItem(event) {
    event.preventDefault();

    // Add the 'active' class to the clicked element and remove it from others
    let target = event.target;
    let items = document.getElementsByClassName('custom-nav-link');

    for (let i = 0; i < items.length; i++) {
        let parentLi = items[i].parentNode; // Get the parent <li> of each <a>
        if (items[i] === target) {
            parentLi.classList.add('active');
        } else {
            parentLi.classList.remove('active');
        }
    }

    // Reset the dropdown toggle text when a non-dropdown-item is clicked
    if (!target.classList.contains('dropdown-item')) {
        const dropdownToggle = document.querySelector('#navbarDropdownMenuLink');
        dropdownToggle.innerText = 'Services';
        localStorage.setItem('dropdownToggleText', 'Services');
    }

    // Now do the navigation
    window.location.href = target.href;
}

function activateDropdownItem(event) {
    event.stopPropagation();  // Prevent the click event from triggering the 'activateNavItem' function

    const dropdownToggle = document.querySelector('#navbarDropdownMenuLink');
    dropdownToggle.innerText = event.target.innerText;
    dropdownToggle.classList.add('active');
    dropdownToggle.parentNode.classList.add('active');

    // Store the new dropdown toggle text in local storage
    localStorage.setItem('dropdownToggleText', event.target.innerText);

    window.location.href = event.target.href;
}

// Set the dropdown toggle text to its stored value when the page is loaded
window.addEventListener('DOMContentLoaded', (event) => {
    const storedDropdownToggleText = localStorage.getItem('dropdownToggleText');
    if (storedDropdownToggleText) {
        const dropdownToggle = document.querySelector('#navbarDropdownMenuLink');
        dropdownToggle.innerText = storedDropdownToggleText;
    }

    const navLinks = document.querySelectorAll('.custom-nav-link');
    navLinks.forEach((link) => {
        link.addEventListener('click', activateNavItem);
    });

    const dropdownItems = document.querySelectorAll('.dropdown-item');
    dropdownItems.forEach((item) => {
        item.addEventListener('click', activateDropdownItem);
    });
});



