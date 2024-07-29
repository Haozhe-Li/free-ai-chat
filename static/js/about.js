var responseElement = document.querySelector(".aboutContent");
responseElement.style.display = "block";

function clearBrowserCache() {
    localStorage.clear();
    sessionStorage.clear();
    var cookies = document.cookie.split("; ");
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    }

    alert("Browser cache cleared successfully!");
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("clear_cache").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent the default link behavior
        clearBrowserCache();
    });
});