(function () {
    var form = document.getElementById("weather-form");
    var btn = document.getElementById("search-btn");
    if (!form || !btn) return;

    form.addEventListener("submit", function () {
        btn.classList.add("is-loading");
    });
})();
