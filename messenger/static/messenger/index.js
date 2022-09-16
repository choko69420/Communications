//TODO: make chat_name dynamic
chat_name = document.getElementById('chat-name').textContent.substring(1, document.getElementById('chat-name').textContent.length - 1);
console.log(chat_name);
var socket = new WebSocket(`ws://${window.location.host}/ws/chat/${chat_name}/`);
socket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var username = data['username'];
    var error = data['error'];
    if (error) {
        console.log(error);
        return false;
    }
    // add message to chat window
    document.querySelector("#chat-log").innerHTML = `<div class="message">
                <div class="message-header">
                    <p class="message-sender">${username} says: ${message}</p>
                </div>
            </div>` + document.querySelector("#chat-log").innerHTML;
};
socket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};
function createChat(event) {
    var chat_name = document.querySelector("#chatName").value;
    // validate chat name
    if (chat_name.length < 1) {
        alert("Chat name must be at least 1 character long");
        return false;
    }
    // if chat_name contains spaces return false
    if (chat_name.includes(" ")) {
        alert("Chat name cannot contain spaces");
        return false;
    }
    var members = document.querySelector("#members").value;
    members = members.split(",");
    var csrf = document.querySelector("#chatName").dataset.csrf;
    fetch("/create_chat", {
        method: "POST",
        body: JSON.stringify({
            chat_name: chat_name,
            members: members
        }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf
        }
    }).then(response => response.json())
    .then(result => {
        console.log(result);
        });
        //clear message input
    document.querySelector("#chatName").value = "";

    // focus on message input
    document.querySelector("#chatName").focus();
    // redirect to chat page
    window.location.href = `/chat/${chat_name}`;
    // stop from submitting the form
    event.preventDefault();
    return false;
}

function messageView(event) {
    // hide create-form div
    document.querySelector("#chat-form").style.display = "none";
    document.querySelector("#chat-log").style.display = "block";
    document.querySelector("#chat_name").style.display = "block";
    // activate send message div
    document.querySelector("#message-form").style.display = "block";
}
function createView(event) {
    // hide send message div
    document.querySelector("#message-form").style.display = "none";
    document.querySelector("#chat-log").style.display = "none";
    document.querySelector("#chat_name").style.display = "none";
    // activate create-form div
    document.querySelector("#chat-form").style.display = "block";

}
function sendMessage(event) {
    var message = document.querySelector("#message").value;
    var username = document.querySelector("#username").value;
    // send message
    // validate message
    if (message.length < 1) {
        alert("Message must be at least 1 character long");
        return false;
    }
    socket.send(JSON.stringify({
        'message': message,
    }));
    // clear message input
    document.querySelector("#message").value = "";
    // focus on message input
    document.querySelector("#message").focus();
    // stop from submitting the form
    event.preventDefault();
    return false;
};
function search(event) {
    var search = document.querySelector("#search").value;
    console.log(search);
    // redirect to search page
    window.location.href = `/chat/${search}`;
    event.preventDefault();
    return false;
}
function Edit(event) {
    var chat_name = document.querySelector("#chat_name_input").value;
    var members = document.querySelector("#chat_members").value;
    // turn members into array
    members = members.split(",");
    //remove all trailing and leading spaces with map
    members = members.map(member => member.trim());
    var csrf = document.querySelector("#chatName").dataset.csrf;
    console.log(chat_name, members, csrf);
    fetch(`/chat/${chat_name}`, {
        method: "POST",
        body: JSON.stringify({
            chat_name: chat_name,
            members: members
        }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf
        }
    }).then(response => response.json())
        .then(result => {
            alert(result);
        }).catch(error => {
            console.log(error);
        });
    event.preventDefault();
}

document.addEventListener("DOMContentLoaded", () => {
    // document.querySelector("#form-send").onsubmit = sendMessage;
    document.querySelector("#send").addEventListener("click", sendMessage);
    document.querySelector("#sendMessage").onclick = messageView;
    document.querySelector("#createChat").onclick = createView;
    // document.querySelector("#form-create").onsubmit = createChat;
    document.querySelector("#create").addEventListener("click", createChat);
    document.querySelector("#search-form").addEventListener('submit', search); 
    document.querySelector("#edit_chat").addEventListener('submit', Edit);
});