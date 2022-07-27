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

const pwinput = $("#password");
const usernameinput = $("#username");
const loginbtn = $("#login");
const signupbtn = $("#signup");

loginbtn.addEventListener("click", function() {
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: usernameinput.value,
      password: pwinput.value
    }),
  })
  .then(res => res.text())
  .then(status => {
    if (status === "Success") {
      localStorage.setItem("username", usernameinput.value);
      localStorage.setItem("password", pwinput.value);
      signupbtn.after(successBox("Successfully logged in!"));
    } else {
      signupbtn.after(errorBox(status));
    }
  });
});

signupbtn.addEventListener("click", function() {
  fetch('/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: usernameinput.value,
      password: pwinput.value
    }),
  })
  .then(res => res.text())
  .then(status => {
    if (status === "Success") {
      localStorage.setItem("username", usernameinput.value);
      localStorage.setItem("password", pwinput.value);
      signupbtn.after(successBox("Successfully signed up!"));
    } else {
      signupbtn.after(errorBox(status));
    }
  });
});