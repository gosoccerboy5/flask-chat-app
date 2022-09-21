const $ = document.querySelector.bind(document);

function createChannelEl(obj) {
  const newEl = document.createElement("div");
  newEl.className = "channel";
  newEl.addEventListener("click", function() {
    window.location.href = "/channel/" + obj.id;
  });
  newEl.innerText = obj.name;
  /*lastPost = document.createElement("span");
  lastPost.className = "lastpost";
  lastPost.innerText = "Last post by " + obj.last_post.username;
  lastPost.title = obj.last_post.date;
  newEl.append(lastPost);*/
  return newEl;
}

if (localStorage.getItem("username") !== null) {
  $("#signedininfo").innerHTML = "<a href='/settings'>You are signed in as " + localStorage.getItem("username") + ".</a>";
}

fetch("/channels")
  .then(res => res.json())
  .then(channels => channels.forEach(channel => {
    $("#channels").append(createChannelEl(channel));
  }));

$("#addChannelBtn").addEventListener("click", function() {
  window.location.assign("/createchannel");
})