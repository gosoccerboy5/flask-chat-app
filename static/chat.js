const $ = document.querySelector.bind(document);

function postTemplate(username, content, date) {
  let el = document.createElement("div");
  el.className = "message";
  el.innerHTML = `<b title="From ${username} at ${date}"><a onclick="window.location.href='/profile?user=${username}'">@${username}</a>:</b><br>${content}`;
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
window.showingNewMessage = false;
function newMessageBox() {
  if (window.showingNewMessage) return;
  const el = errorBox("You have new messages");
  el.style.background = "greenyellow";
  el.style.position = "fixed";
  el.style.left = "45%";
  el.style.top = "10%";
  el.children[0].addEventListener("click", () => window.showingNewMessage = false);
  document.body.append(el);
  window.showingNewMessage = true;
}

if (localStorage.getItem("username") !== null) {
  $("#signedininfo").innerHTML = "<a href='/settings'>You are signed in as " + localStorage.getItem("username") + ".</a>";
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
  }/*
  const body = JSON.stringify({
    content: input.value,
    username: localStorage.getItem("username"),
    password: localStorage.getItem("password"),
    channelId,
  });
  fetch('/postmessage', {
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
      updateMsgs(true);
      input.value = "";
    }
  })
  .catch((error) => {
    console.error('Error:', error);
  });*/
  canSubmit = false;
  setTimeout(() => canSubmit = true, 200);
  window.ws.send(JSON.stringify({"username": localStorage.getItem("username"), content: input.value}));
}

btn.addEventListener("click", submit);
input.addEventListener("keydown", (evt) => {
  if (evt.keyCode === 13) {
    submit();
  }
});

var msgs = [];

const msgsEl = $("#msgs");
fetch('/messages/' + channelId)
  .then(res => res.json())
  .then(res => msgs = res)
  .then(msgs => msgs.forEach(msg => {
    msgsEl.append(
      postTemplate(msg.username, msg.content, msg.date));
  }))
  .then(() => {
    window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: "smooth"});
  })
  .then(() => window.setInterval(console.log, 1000));


function updateMsgs(own = false) {
  fetch('/chatcount/' + channelId)
    .then(res => res.json())
    .then(res => res["count"])
    .then(count => {
      if (msgs.length < count) {
        fetch('/messages/' + channelId)
          .then(res => res.json())
          .then(allmsgs => {
            const nearBottom = document.documentElement.scrollHeight - document.body.scrollTop < 1000;
            const newMsgs = allmsgs.slice(msgs.length);
            newMsgs.forEach(msg => {
              msgsEl.append(
                postTemplate(msg.username, msg.content, msg.date));
            });
            msgs = allmsgs;
            if (!nearBottom && newMsgs.some(msg => msg.username !== localStorage.getItem("username"))) {
              newMessageBox();
            } else {
              window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: "smooth"});
            }
          });
      }
    });
}


window.addEventListener("load", function() {
  channelNum = Number(location.href.match(/\d+$/)[0]);
  window.ws = new WebSocket("wss://" + location.host + "/channelws");
  ws.addEventListener("open", function(event) {
    ws.send(JSON.stringify({
      channel: channelNum,
    }));
  });
  ws.addEventListener("message", function(event) {
    let postData = JSON.parse(event.data);
    msgsEl.append(postTemplate(postData.username, postData.content, postData.date));
    console.log(event.data);
  });
});