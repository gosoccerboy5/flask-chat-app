const $ = document.querySelector.bind(document);

function postTemplate(username, content, date) {
  let el = document.createElement("div");
  el.className = "message";
  el.innerHTML = `<b title="From ${username} at ${date}">@${username}:</b><br>${content}`;
  return el;
}
function errorBox(text) {
  const el = document.createElement("div");
  el.innerText = text;
  el.className = "err";
  el.innerHTML += '<span onclick="this.parentNode.parentNode.removeChild(this.parentNode);" class="close" title="close">✖</span>';
  el.style.margin = "auto";
  return el;
}

if (localStorage.getItem("username") !== null) {
  $("#signedininfo").innerText = "You are signed in as " + localStorage.getItem("username") + ".";
}


const btn = $("#btn");
const input = $("#input");

let canSubmit = true;

function submit() {
  if (!canSubmit) {
    $("#msgs").append(errorBox("Woah there, looks like you're chatting a little fast. Wait a little bit longer before posting each message."));
    return;
  }
  if (input.value.trim() === "") {
    return;
  }
  if (localStorage.getItem("username") === null) {
    $("#msgs").append(errorBox("You are not signed in. Head over to the login page to sign up or login."));
    return;
  }
  const body = JSON.stringify({
    content: input.value,
    date: Date().replace(/[a-z]+-\d+ /i, ""),
    username: localStorage.getItem("username"),
    password: localStorage.getItem("password"),
  });
  fetch('/chats', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body,
  })
  .then(res => res.text())
  .then((res) => {
    if (res !== "Success") {
      $("#msgs").append(errorBox(res));
    } else {
      updateMsgs();
      input.value = "";
    }
  })
  .catch((error) => {
    console.error('Error:', error);
  });
  canSubmit = false;
  setTimeout(() => canSubmit = true, 200);
}

btn.addEventListener("click", submit);
input.addEventListener("keydown", (evt) => {
  if (evt.keyCode === 13) {
    submit();
  }
});

var msgs = [];

const msgsEl = $("#msgs");
fetch('/chats')
  .then(res => res.text())
  .then(res => msgs = JSON.parse(res))
  .then(msgs => msgs.forEach(msg => {
    msgsEl.append(
      postTemplate(msg.username, msg.content, msg.date));
  }))
  .then(() => {
    window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: "smooth"});
  });


function updateMsgs() {
  fetch('/chatcount')
    .then(res => res.text())
    .then(res => Number(res))
    .then(count => {
      if (msgs.length < count) {
        fetch('/chats')
        .then(res => res.text())
        .then(res => JSON.parse(res))
        .then(allmsgs => {
          allmsgs.slice(msgs.length).forEach(msg => {
            msgsEl.append(
              postTemplate(msg.username, msg.content, msg.date));
          });
          msgs = allmsgs;
          });
      }
    });
}

window.setInterval(updateMsgs, 1000);