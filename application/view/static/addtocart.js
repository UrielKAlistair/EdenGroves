function addToCart(product_id) {

    const formData = new FormData();
    formData.append("product_id", product_id);
    fetch("/addcart", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                const es = document.getElementById("success-msg")
                magicFade(es, "");

                const ee = document.getElementById("error-msg")
                magicFade(ee, "Product Already in Cart")
            } else if (data.success) {
                const es = document.getElementById("success-msg")
                magicFade(es, "Added to Cart Successfully");

                const ee = document.getElementById("error-msg")
                magicFade(ee, "")
            }
            else if (data.redirect){
                window.location.href = data.redirect;
            }
        })
        .catch(() => {
            const e = document.getElementById("error-msg");
            magicFade(e, "We're experiencing issues; Please Try again later.");
        });
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
