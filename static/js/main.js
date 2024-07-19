var message = ""
var submessage = ""
document.addEventListener("DOMContentLoaded", function () {
  document.querySelector("form").onsubmit = function (e) {
    e.preventDefault();
    var startTime = Date.now();
    response.style.display = "none";
    var inputText = document.getElementById("input_text").value;
    if (
      !inputText ||
      !document.querySelector('input[name="model"]:checked')
    ) {
      var responseElement = document.querySelector(".response");
      responseElement.textContent = "Please fill in the input text and select a model";
      responseElement.style.display = "block";
      return;
    }
    var model = document.querySelector(
      'input[name="model"]:checked'
    ).value;

    var generatingTimeout = setTimeout(function () {
      var responseElement = document.querySelector(".response");
      responseElement.textContent = "Still generating...";
      responseElement.style.display = "block";
    }, 2000);

    fetch("/generate", {
      method: "POST",
      body: new URLSearchParams({ input_text: inputText, model: model }),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        clearTimeout(generatingTimeout);
        var endTime = Date.now();
        var duration = endTime - startTime;
        var responseElement = document.querySelector(".response");
        responseElement.style.display = "block  ";
        if (data.error) {
          responseElement.textContent =
            "Error Occured in Frontend, Error Code: 401";
        } else {
          message = data.response;
          submessage = `<i style="color: gray;">${model} is ready in ${duration} ms⚡️</i>`
          responseElement.innerHTML = submessage + "<br><br>" + message;
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        clearTimeout(generatingTimeout); // Clear the timeout in case of error
      });
  };

  document.querySelector(".response").onclick = function () {
    if (message == "") {
      return;
    }
    submessage = "<i style='color: gray;'>Copied ✅</i>";
    navigator.clipboard.writeText(message).then(function () {
      document.querySelector(".response").innerHTML = submessage + "<br><br>" + message;
    }).catch(function (error) {
      console.error("Copy Error: ", error);
    });
  };
});