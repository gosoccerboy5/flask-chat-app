const $ = document.querySelector.bind(document);
const title = $("#title"), submit = $("#submit");
if (localStorage.getItem("username") !== null) {
  $("#signedininfo").innerHTML = "<a href='/settings'>You are signed in as " + localStorage.getItem("username") + ".</a>";
}
function errorBox(text) {
  const el = document.createElement("div");
  el.innerText = text;
  el.className = "err";
  el.innerHTML += '<span onclick="this.parentNode.parentNode.removeChild(this.parentNode);" class="close" title="close">✖</span>';
  return el;
}
submit.addEventListener("click", function() {
  fetch('/createchannel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "username": localStorage.getItem("username"),
      "title": $("#title").value, 
      "password": localStorage.getItem("password")
    })
  }).then(res => res.json())
    .then(res => {
      if (res.status === "Success") {
        window.location.replace("/channel/" + res.message);
      } else {
        submit.after(errorBox(message));
      }
    });
});