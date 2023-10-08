from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile, User, Skill
from django.contrib.auth import logout, login, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import ProfileForm, CustomUserCreationForm, SkillForm, MessageForm
from .utils import search_profiles


def login_user(request):
    if request.user.is_authenticated:
        return redirect('profiles')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            messages.error(request, 'Такого пользователя не существует')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profiles')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'users/login_register.html')


def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower().strip()
            user.save()
            messages.success(request, 'Аккаунт был создан')
            login(request, user)
            return redirect('profiles')

    return render(request, 'users/login_register.html', {'page': page, 'form': form})


def profiles(request):
    profs, search_query = search_profiles(request)
    context = {'profiles': profs, 'search_query': search_query}
    return render(request, 'users/index.html', context)


def user_profile(request, pk):
    profile = Profile.objects.get(pk=pk)
    top_skills = profile.skill_set.exclude(description__exact='')
    other_skills = profile.skill_set.filter(description__exact='')
    context = {
        'top_skills': top_skills,
        'other_skills': other_skills,
    }
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def user_account(request):
    prof = request.user.profile
    skills = prof.skill_set.all()
    projects = prof.project_set.all()
    context = {
        'profile': prof,
        'skills': skills,
        'projects': projects,
    }

    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def edit_account(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            messages.success(request, 'Account edited successfully!')
            return redirect('account')
    return render(request, 'users/profile_form.html', {'form': form})


@login_required(login_url='login')
def create_skill(request):
    profile = request.user.profile
    form = SkillForm()

    if request.method == "POST":
        skill = form.save(commit=False)
        skill.owner = profile
        skill.save()

        messages.success(request, 'Скилл был успешно добавлен')

        return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def update_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(pk=pk)
    form = SkillForm(instance=skill)

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Скил был успешно добавлен')

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def delete_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(pk=pk)

    if request.method == 'POST':
        skill.delete()
        return redirect('account')

    context = {'skill': skill}

    return render(request, 'projects/delete.html', context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    user_messages = profile.messages.all()
    unread_count = user_messages.filter(is_read=False).count()
    context = {'user_messages': user_messages,
               'unread_count': unread_count}
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def view_message(request, pk):
    profile = request.user.profile
    message = profile.messages.get(pk=pk)
    if not message.is_read:
        message.is_read = True
        message.save()

    context = {'message': message}
    return render(request, 'users/message.html', context)


def create_message(request, pk):
    recipient = Profile.objects.get(pk=pk)
    form = MessageForm()
    sender = None
    if request.user.is_authenticated:
        del form.fields['name']
        del form.fields['email']
        sender = request.user.profile

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email

            messages.success(request, 'Ваше сообщение отправлено успешно!')
            message.save()

            return redirect('user_profile', pk=recipient.id)
    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)