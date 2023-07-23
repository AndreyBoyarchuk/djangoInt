document.addEventListener("DOMContentLoaded", function() {
    let navItems = document.querySelectorAll(".nav-link");

    navItems.forEach(function(item) {
      item.addEventListener("click", function(event) {
        event.preventDefault();

        let currentlyActive = document.querySelector(".nav-link.active");
        if (currentlyActive) {
          currentlyActive.classList.remove("active");
        }

        event.target.classList.add("active");
      });
    });
});
