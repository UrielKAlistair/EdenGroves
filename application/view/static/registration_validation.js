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

function validatePassword(password) {
    var length = password.length;
    var errors = [];

    if (length < 12 || length > 25) {
        errors.push("The entered password is not of the correct length.");
    }
    if (!/[A-Z]/.test(password)) {
        errors.push("The entered password does not have an Uppercase letter.");
    }
    if (!/[a-z]/.test(password)) {
        errors.push("The entered password does not have a Lowercase letter.");
    }
    if (!/\d/.test(password)) {
        errors.push("The entered password does not have a number.");
    }
    if (!/[!@#$%^&*]/.test(password)) {
        errors.push("The entered password does not have a special character.");
    }
    if (password.includes(' ')) {
        errors.push("Spaces are not allowed in the password.");
    }
    return errors
}

const validateEmail = (email) => {
    return String(email)
        .toLowerCase()
        .match(
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        );
};

window.addEventListener("DOMContentLoaded", () => {
    document.getElementById("reg-form").addEventListener("submit", function (event) {

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const password2 = document.getElementById("confirm_password").value;

            const pwderror = document.getElementById("pwd_error");
            const emailerror = document.getElementById("email_error");

            let messages = validatePassword(password);
            if (password !== password2) {
                messages.push("Passwords do not match.");
            }

            if (messages.length !== 0) {
                magicFade(pwderror, messages.join(("\r\n")));
                event.preventDefault();
            }
            else{
                magicFade(pwderror, "")
            }
            if (!validateEmail(email)) {
                magicFade(emailerror, "The entered email is not valid.")
                event.preventDefault();
            }
            else{
                magicFade(emailerror, "")
            }
        }
    )
});



