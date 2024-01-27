function myFunction(event) {
    event.preventDefault();
    const product_id = event.target.id;
    const quantity = event.target.querySelector('input').value;

    const formData = new FormData();
    formData.append("product_id", product_id);
    formData.append("product_count", quantity);

    fetch("/change_product_count", {
        method: "POST",
        body: formData
    }).then(response => response.json())
        .then(data => {
            if (data.error) {
                const f = document.getElementById("success-msg");
                magicFade(f, '');

                const e = document.getElementById("error-msg");
                magicFade(e, data.error);

            } else {
                const f = document.getElementById("error-msg");
                magicFade(f, '');

                const e = document.getElementById("success-msg");
                magicFade(e, data.success);

                const price = Number(document.getElementById("p" + product_id).textContent.substring(1));
                const subtotal = document.getElementById("t" + product_id);
                const total = document.getElementById("total-price");

                const newsubtotal = price * Number(quantity);
                const newtotal = Number(total.textContent.substring(1)) - Number(subtotal.textContent.substring(1)) + newsubtotal;
                magicFade(total, "₹" + newtotal);
                magicFade(subtotal, "₹" + newsubtotal);
            }
        })
}

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
    var elements = document.getElementsByClassName("update-count");

    Array.from(elements).forEach(function (element) {
        element.addEventListener("submit", myFunction);
    });
})