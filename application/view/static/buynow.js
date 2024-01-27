window.addEventListener("DOMContentLoaded", () => {
    const quantity = document.getElementById("pq")
    quantity.addEventListener("change", function (event) {
        document.getElementById("total").value = (Number(quantity.value) * Number(document.getElementById("price").value))
    });
})