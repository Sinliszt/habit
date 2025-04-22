from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import User, Habit, HabitLog, FriendRequest
from .forms import HabitForm, HabitLogForm

User = get_user_model()

@login_required
def index(request):
    habits = Habit.objects.filter(users=request.user)
    habit_data = []

    for habit in habits:
        logs=habit.logs.filter(user=request.user).order_by('-date')
        today_done = logs.filter(date=date.today()).exists()

        current_streak = 0
        longest_streak = 0
        streak = 0
        seen_dates = set(log.date for log in logs)
        day = date.today()
        while day in seen_dates:
            streak += 1
            day -= timedelta(days=1)
        current_streak = streak

        streak = 0
        for i in range((date.today() - habit.created_at).days + 1):
            day = habit.created_at + timedelta(days = i)
            if day in seen_dates:
                streak += 1
                longest_streak = max(longest_streak, streak)
            else:
                streak = 0

        habit_data.append({
            "habit": habit,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "today_done": today_done,
        })

    return render(request, "tracker/index.html", {
        "habit_data": habit_data,
    })


@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, users=request.user)
    logs = habit.logs.order_by('-date')
    today_done = logs.filter(user=request.user, date=date.today()).exists()
    streak_data = get_streaks_and_progress(request.user, habit)
    if request.method == 'POST':
        form = HabitLogForm(request.POST)
        if form.is_valid():
            note = form.cleaned_data['note']
            HabitLog.objects.update_or_create(
                habit=habit,
                user=request.user,
                date=date.today(), 
                defaults={
                    'note': note
                })
            return redirect('habit_detail', habit_id=habit.id)
    else:
        try:
            note = habit.logs.get(user=request.user, date=date.today()).note
        except HabitLog.DoesNotExist:
            note = ""
        form = HabitLogForm(initial={
        "note": note,
        })

    return render(request, 'tracker/habit_detail.html', {
        "habit": habit,
        "logs": logs,
        "today_done": today_done,
        "form": form,
        "streak": streak_data,
    })

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tracker/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tracker/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not username or not email or not password:
            return render(request, "tracker/register.html", {
                "message": "All fields are required."
            })
        
        if password != confirmation:
            return render(request, "tracker/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "tracker/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tracker/signup.html")

@login_required
def create_habit(request):
    if request.method == "POST":
        form = HabitForm(request.POST, user=request.user)
        if form.is_valid():
            habit=form.save(commit=False)
            habit.save()
            form.save_m2m()
            habit.users.add(request.user)
            return redirect('index')
    else:
        form = HabitForm(user=request.user)

    return render(request, "tracker/create_habit.html", {
        "form": form
    })

@require_POST
@login_required
def log_shared_habit(request):
    habit_id = request.POST.get("habit_id")
    try:
        habit = Habit.objects.get(id=habit_id, users=request.user)
        log, created = HabitLog.objects.update_or_create(
            habit=habit,
            user=request.user,
            date=date.today(),
            defaults = {
                "note": request.POST.get("note", "")
            }
        )
        return JsonResponse({
            "status": "success",
            "message": "Habit Logged!",
            "today": date.today().isoformat(),
            "user": request.user.username,
        })
    except Habit.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Habit not found",
        }, status=404
        )

def get_streaks_and_progress(user, habit):
    logs = HabitLog.objects.filter(user=user, habit=habit).order_by("-date")
    today = date.today()
    current_streak = 0
    longest_streak = 0
    streak = 0
    last_date = None
    
    all_dates = set(log.date for log in logs)

    for i in range((today - habit.created_at).days + 1):
        t = today - timedelta(days=i)
        if t in all_dates:
            streak +=1
            if i == 0:
                current_streak = streak
            else:
                if i == 0:
                    continue
                longest_streak = max(longest_streak, streak)
                streak = 0

            
            longest_streak = max(longest_streak, streak)
            total_days = (today-habit.created_at).days + 1
            completion_percent = round((len(all_dates) / total_days)*100,1)

            return {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "completion_percent": completion_percent,
            }


@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect("search_users")

@login_required
def accept_friend_request(request, request_id):
    friends = request.user.friends.all()
    incoming = FriendRequest.objects.filter(to_user=request.user)
    outgoing = FriendRequest.objects.filter(from_user=request.user)

    return render(request, "tracker/friends_list.html", {
        "friends": friends,
        "incoming": incoming,
        "outgoing": outgoing,
    })

@login_required
def search_users(request):
    query = request.GET.get("q")
    users=[]
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)

    return render(request, "tracker/friend_search.html", {
        "users": users,
        "query": query,
    })

@login_required
def friends_list(request):
    friends = request.user.friends.all()
    return render(request, "tracker/friends_list.html", {
        "friends": friends,
    })