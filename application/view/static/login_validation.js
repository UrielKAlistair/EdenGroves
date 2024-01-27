function myFadeOutFunction(opacity, e, replacement) {
    if (opacity >= 0.1) {
        opacity -= .1;
        e.style.opacity = opacity;
        setTimeout(function () {
            myFadeOutFunction(opacity, e, replacement)
        }, 10);
    } else {
        e.textContent = replacement;
        myFadeInFunction(0, e);
    }
}

function myFadeInFunction(opacity, e) {
    if (opacity <= 0.9) {
        opacity += .1;
        e.style.opacity = opacity;
        setTimeout(function () {
            return myFadeInFunction(opacity, e);
        }, 10);
    } else {
        return true;
    }
}

function magicFade(elem, replacement) {
    if (elem.textContent !== "") {
        myFadeOutFunction(1, elem, replacement);
    } else {
        elem.textContent = replacement;
        myFadeInFunction(0, elem);
    }
}

window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("login-form").addEventListener("submit", function (event) {
        event.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        fetch("/validate_login", {
            method: "POST",
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    const e = document.getElementById("error-msg")
                    magicFade(e, data.error)
                } else {
                    window.location.replace("/");
                }
            })
            .catch(() => {
                const e = document.getElementById("error-msg");
                magicFade(e, "We're experiencing issues; Please Try again later.");
            });
    });
});