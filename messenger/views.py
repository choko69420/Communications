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
    chat = Chat.objects.filter(name="general").first()
    # make the chat avaliable to all users
    if chat is None:
        chat = Chat.objects.create(name="general")
        chat.save()
    chat.users.add(request.user)
    messages = chat.messages.all().order_by('-timestamp')
    members = User.objects.all()
    # make members a list of usernames
    members = [member.username for member in members]
    # make member into a string
    members = ', '.join(members)
    avalible_chats = Chat.objects.filter(users=request.user).all()
    context = {
        'chat': chat,
        'messages': messages,
        'avalible_chats': avalible_chats,
    }
    return render(request, 'messenger/index.html', context)


@login_required(login_url='/login')
def create_chat(request):
    if request.method == "POST":
        body = request.body
        data = json.loads(body)
        sender = request.user
        members = [User.objects.filter(username__iexact=username).first()
                   for username in data["members"]]
        if not sender in members:
            members.append(sender)
        chat = Chat(name=data["chat_name"], creator=sender)
        chat.save()
        for member in members:
            chat.users.add(member)
        return JsonResponse({"message": "Chat created successfully."}, status=201)
    else:
        return JsonResponse({'error': 'POST request required.'}, status=400)


@login_required(login_url='/login')
def chat(request, chat_name):
    chat = Chat.objects.filter(name=chat_name).first()
    # check if chat exists
    if not chat:
        return render(request, 'messenger/404.html', status=404)
    if request.method == "GET":
        # check if user is in chat
        members = chat.users.all()
        # make members a list of usernames
        members = [member.username for member in members]
        # make member into a string
        members = ', '.join(members)
        if request.user in chat.users.all():
            messages = chat.messages.all().order_by('-timestamp')
            context = {
                'chat': chat,
                'messages': messages,
                'members': members
            }
            return render(request, 'messenger/index.html', context)
        else:
            return JsonResponse({'error': 'You are not in this chat.'}, status=403)
    else:
        # Edit chat
        # get the data
        body = request.body
        data = json.loads(body)
        # get the chat
        chat = Chat.objects.filter(name=chat_name).first()
        if not chat:
            return JsonResponse({'error': 'Chat not found.'}, status=404)
        # check if user is creator
        if request.user != chat.creator:
            return JsonResponse({'error': 'You are not the creator of this chat.'}, status=403)
        # if the user is the creator, edit the chat
        chat.name = data["chat_name"]
        # set the members to the new members
        members = [User.objects.filter(
            username__iexact=username).first() for username in data["members"]]
        # add the creator to the members
        if not request.user in members:
            members.append(request.user)
        # remove all the old members
        chat.users.all()
        # add the new members
        for member in members:
            chat.users.add(member)
        chat.save()
        return JsonResponse({"message": "Chat edited successfully."}, status=200)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "messenger/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "messenger/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "messenger/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "messenger/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "messenger/register.html")
