from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordResetDoneView
)
from django.urls import reverse_lazy
from .models import Task
from datetime import datetime
import speech_recognition as sr
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count


# 🔹 AUTO CATEGORY DETECTION
def detect_category(title):
    title = title.lower()

    if any(word in title for word in ['read', 'reading', 'book', 'novel', 'story']):
        return 'reading'

    if any(word in title for word in ['write', 'writing', 'notes', 'essay', 'article']):
        return 'writing'

    if any(word in title for word in ['play', 'game', 'music', 'dance', 'hobby']):
        return 'hobbies'

    return 'daily'


# 🔹 DASHBOARD
@login_required
def dashboard(request):
    category_filter = request.GET.get('category')

    if category_filter:
        tasks = Task.objects.filter(user=request.user, category=category_filter)
    else:
        tasks = Task.objects.filter(user=request.user)

    # 📊 Category stats
    category_data = (
        Task.objects
        .filter(user=request.user)
        .values('category')
        .annotate(count=Count('id'))
    )

    categories = [item['category'] for item in category_data]
    category_counts = [item['count'] for item in category_data]

    context = {
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(completed=True).count(),
        'pending_tasks': tasks.filter(completed=False).count(),
        'selected_category': category_filter,
        'categories': categories,
        'category_counts': category_counts,
    }

    return render(request, 'todo/dashboard.html', context)


# 🔹 ADD TASK
@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        deadline = request.POST.get('deadline')

        if title:
            category = detect_category(title)  # 🔥 AUTO CATEGORY

            task = Task(
                user=request.user,
                title=title,
                category=category
            )

            if deadline:
                try:
                    task.deadline = datetime.fromisoformat(deadline)
                except Exception:
                    pass

            task.save()

    return redirect('todo:dashboard')


# 🔹 EDIT TASK
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.category = request.POST.get('category', task.category)

        deadline = request.POST.get('deadline')
        if deadline:
            try:
                task.deadline = datetime.fromisoformat(deadline)
            except Exception:
                pass

        task.save()
        return redirect('todo:dashboard')

    return render(request, 'todo/edit_task.html', {'task': task})


# 🔹 COMPLETE TASK
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect('todo:dashboard')


# 🔹 DELETE TASK
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('todo:dashboard')


# 🔹 AUDIO TO TEXT
@login_required
def audio_to_text(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(request.FILES['audio_file']) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)
            return JsonResponse({'success': True, 'text': text})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'todo/audio_to_text.html')


# 🔹 SIGNUP
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('todo:signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('todo:signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully")
        return redirect('todo:login')

    return render(request, "todo/signup.html")


# 🔹 LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('todo:dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "todo/login.html")


# 🔹 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('todo:login')


# 🔹 PASSWORD RESET
class CustomPasswordResetView(PasswordResetView):
    template_name = 'todo/password_reset.html'
    email_template_name = 'todo/password_reset_email.html'
    subject_template_name = 'todo/password_reset_subject.txt'
    success_url = reverse_lazy('todo:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'todo/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'todo/password_reset_confirm.html'
    success_url = reverse_lazy('todo:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'todo/password_reset_complete.html'