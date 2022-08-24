const $ = document.querySelector.bind(document);

function errorBox(text) {
  const el = document.createElement("div");
  el.innerText = text;
  el.className = "err";
  el.innerHTML += '<span onclick="this.parentNode.parentNode.removeChild(this.parentNode);" class="close" title="close">✖</span>';
  return el;
}
function successBox(text) {
  const el = errorBox(text);
  el.setAttribute("class", "success");
  return el;
}

const bio = $("#bio");
const submit = $("#submit");

submit.addEventListener("click", function() {
  fetch("/set_settings", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: localStorage.getItem("username"),
      password: localStorage.getItem("password"),
      bio: bio.value,
    }),
  })
    .then(res => res.text())
    .then(res => {
      if (res === "Success") {
        submit.after(successBox("Successfully updated settings"));
      } else {
        submit.after(errorBox(res));
      }
    })
});

fetch("/user_data?user=" + localStorage.getItem("username"))
  .then(res => res.json())
  .then(data => bio.value = data["bio"]);