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
  },
  "generating": {
    "en": "Your response will be ready in a few seconds...",
    "zh-CN": "您的回答将在几秒钟内准备好...",
    "ja": "回答は数秒で準備されます..."
  },
  "rag_generating": {
    "en": "Collecting information from the Internet,\nthis may take a about 15 seconds...",
    "zh-CN": "正在联网收集信息，\n这可能需要大约15秒...",
    "ja": "インターネットから情報を収集しています、\n約15秒かかる場合があります..."
  },
  "noresponse": {
    "en": "No response from the server, please try again later",
    "zh-CN": "服务器未响应，请稍后重试",
    "ja": "サーバーからの応答がありません、後でもう一度お試しください"
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
    var enableRag = document.getElementById("enabled_rag").checked;

    if (!enableContext) {
      chatHistory = [];
    } else {
      if (chatHistory.length > 8) {
        chatHistory = chatHistory.slice(chatHistory.length - 8);
      }
    }

    var slowGenerating = setTimeout(function () {
      responseElement.textContent = enableRag ? warningMessages["rag_generating"][pageLanguage] : warningMessages["generating"][pageLanguage];
      responseElement.style.display = "block";
    }, 2000);

    var NoResponseTimeout = setTimeout(function () {
      responseElement.textContent = warningMessages["noresponse"][pageLanguage];
      responseElement.style.display = "block";
    }, 30000);

    fetch("/generate", {
      method: "POST",
      body: new URLSearchParams({ input_text: inputText, model: model, context: JSON.stringify(chatHistory), rag: enableRag }),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        clearTimeout(slowGenerating);
        clearTimeout(NoResponseTimeout);
        var endTime = Date.now();
        var duration = endTime - startTime;
        var responseElement = document.querySelector(".response");
        responseElement.style.display = "block  ";
        if (data.error) {
          responseElement.textContent =
            "Error Occured in Frontend, Error Code: 401";
        } else {
          message = data.response;
          submessage = `<i style="color: gray;">Our AI is ready in ${duration} ms⚡️</i>`
          responseElement.innerHTML = submessage + "<br><br>" + message;
          if (enableContext && !message.startsWith("Error")) {
            updateChatHistory({ "role": "user", "content": inputText });
            updateChatHistory({ "role": "assistant", "content": message });
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        clearTimeout(slowGenerating);
        clearTimeout(NoResponseTimeout);
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