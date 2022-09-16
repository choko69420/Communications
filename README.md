# Communications

## Installation
- first install the packages
  ``` pip3 install -r requirements.txt ```
- run the docker redis server
  ``` docker run -p 6379:6379 -d redis:5 ```
- make migrations
  ``` python3 manage.py makemigrations ```
- migrate
  ``` python3 manage.py migrate ```

- run the server
  ``` python3 manage.py runserver ```

# Distinctiveness and Complexity
- The project is a chat application that allows users to chat with each other in real time.

- the project is complex because it uses websockets (django channels) and REST API to communicate with the server.

- the project is distinct because generally chat applications are not built with django.

- the application is a different from my previous chat projects because it saves the messages in the database and it is not a single page application.

- although the project is not a single page application, it is still a SPA because it uses websockets to communicate with the server.

- my application is mobile friendly because it uses bootstrap and it is responsive.

- the project is may be tweaked in a way that it can easily be deployed on your home network.
  
# Explaining the code
- the project uses redis as the channel layer.
  `communications/asgi.py`
``` python
import messenger.routing
import os


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'communications.settings')
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                messenger.routing.websocket_urlpatterns
            )
        )
    ),
    # Just HTTP for now. (We can add other protocols later.)
})
```
- the project uses django channels to communicate with the server.
  `messenger/consumers.py`
``` python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User, Chat, Message
#import sync_to_async
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ... # get chat_name from url
        # check if user is in chat for validation
        ... 
        # define a user for each channel (websocket)
        ... # Join room group

    async def disconnect(self, close_code):
        ... # Leave room group

    # Receive message from WebSocket
    async def receive(self, text_data):
        ... # receive message from user client
        # check if chat exists asynchronusly
        if await database_sync_to_async(chat.exists)():
            ... #get chat object
            def check_user(user): ... # check if user is in chat for validating server-side
            if user_in_chat:
                ... # save message to database
                ... # Send message to room group
            else:
              ... # send error message to user that they are not in the chat
        else:
          ... # send error message to user that the chat does not exist

    async def chat_message(self, event):
        ... # Send message to all other users in the chat
```

- the project uses django rest framework to communicate with the server.
  `messenger/views.py`
``` python
from sqlite3 import IntegrityError
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from .models import User, Chat, Message
import json


@login_required(login_url='/login')
def index(request):
    # default chat name is general 
    # although this is fixed it can be changed
    chat = Chat.objects.filter(name="general").first()
    if chat is None:
      ... # create chat
    # make the chat avaliable to all users
    ...
    # get all the messages in the chat
    ...
    # get all the chats the user is in
    ...
    context = {
        'chat': chat,
        'messages': messages,
        'avalible_chats': avalible_chats,
    }
    return render(request, 'messenger/index.html', context)


@login_required(login_url='/login')
def create_chat(request):
    if request.method == "POST":
      ... #creates a chat with validation
    else:
      #needs to be a post request
        return JsonResponse({'error': 'POST request required.'}, status=400)


@login_required(login_url='/login')
def chat(request, chat_name):
    chat = Chat.objects.filter(name=chat_name).first()
    # check if chat exists
    if not chat:
        return render(request, 'messenger/404.html', status=404)
    if request.method == "GET":
      ... #validate user is in chat
      ... #get all the messages in the chat
      ... #get all the chats the user is in
      context = {
          'chat': chat,
          'messages': messages,
          'avalible_chats': avalible_chats,
      }
      return render(request, 'messenger/index.html', context)
    else:
        # Edit chat
        ... # check if chat exists
        if not chat:
            return JsonResponse({'error': 'Chat not found.'}, status=404)
        ... # check if user is creator 
        # if the user is the creator, edit the chat
        ... 
        return JsonResponse({"message": "Chat edited successfully."}, status=200)

# same implementation as other projects but username is unique
def login_view(request):
    ...

def logout_view(request):
    ...
def register(request):
    ...
```
- the project uses django models to store data in the database.
  in `messenger/models.py`

# Additional information
I had to read the docs for django channels and learn more about docker to be able to set up this project and finish it.
