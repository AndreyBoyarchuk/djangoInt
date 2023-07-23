document.addEventListener("DOMContentLoaded", function() {
    var navItems = document.querySelectorAll(".nav-link");

    navItems.forEach(function(item) {
      item.addEventListener("click", function(event) {
        event.preventDefault();

        var currentlyActive = document.querySelector(".nav-link.active");
        if (currentlyActive) {
          currentlyActive.classList.remove("active");
        }

        event.target.classList.add("active");
      });
    });
  });