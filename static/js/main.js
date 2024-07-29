var message = ""
var submessage = ""
var pageLanguage = document.querySelector("html").lang;
var chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

function updateChatHistory(newMessage) {
  chatHistory.push(newMessage);
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

var warningMessages = {
  "noinput": {
    "en": "Please enter some text",
    "zh-CN": "请输入一些文本",
    "ja": "テキストを入力してください"
  },
  "longinput": {
    "en": "Input text is too long, please keep it under 512 characters",
    "zh-CN": "输入文本太长，请保持在512个字符以下",
    "ja": "入力テキストが長すぎます。512文字以下にしてください"
  },
  "nomodel": {
    "en": "Please select a model",
    "zh-CN": "请选择一个模型",
    "ja": "モデルを選択してください"
  }
};
document.addEventListener("DOMContentLoaded", function () {
  document.querySelector("form").onsubmit = function (e) {
    e.preventDefault();
    var startTime = Date.now();
    response.style.display = "none";
    var responseElement = document.querySelector(".response");
    var inputText = document.getElementById("input_text").value;
    if (
      !inputText
    ) {
      responseElement.textContent = warningMessages["noinput"][pageLanguage];
      responseElement.style.display = "block";
      return;
    }
    if (inputText.length > 512) {
      responseElement.textContent = warningMessages["longinput"][pageLanguage];
      responseElement.style.display = "block";
      return;
    }
    if (!document.querySelector('input[name="model"]:checked')) {
      responseElement.textContent = warningMessages["nomodel"][pageLanguage];
      responseElement.style.display = "block";
      return;
    }

    var model = document.querySelector(
      'input[name="model"]:checked'
    ).value;

    var enableContext = document.getElementById("enabled_context").checked;

    if (!enableContext) {
      chatHistory = [];
    } else {
      if (chatHistory.length > 8) {
        chatHistory = chatHistory.slice(chatHistory.length - 8);
      }
    }

    var generatingTimeout = setTimeout(function () {
      responseElement.textContent = "Still generating...";
      responseElement.style.display = "block";
    }, 2000);

    fetch("/generate", {
      method: "POST",
      body: new URLSearchParams({ input_text: inputText, model: model, context: JSON.stringify(chatHistory) }),
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
          if (enableContext) {
            updateChatHistory({ "role": "user", "content": inputText });
            updateChatHistory({ "role": "assistant", "content": message });
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        clearTimeout(generatingTimeout);
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