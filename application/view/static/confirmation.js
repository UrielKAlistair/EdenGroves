window.addEventListener("DOMContentLoaded", () => {
    var forms = document.getElementsByClassName("danger-form");

    Array.from(forms).forEach(function (element) {
        element.addEventListener("submit", confirmSubmission);
    });

    var buttons = document.getElementsByClassName("danger-button");

    Array.from(buttons).forEach(function (element) {
        element.addEventListener("click", confirmSubmission);
    });

});
function confirmSubmission(event) {
    if (!confirm("Are you sure ?")){
        event.preventDefault();
    }

}

