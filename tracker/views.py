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
from .utils import calculate_streaks

User = get_user_model()

@login_required
def index(request):
    habits = Habit.objects.filter(users=request.user)
    habit_data = []

    for habit in habits:
        logs=habit.logs.filter(user=request.user).order_by('-date')
        today_done = logs.filter(date=date.today()).exists()

        streak_data = calculate_streaks(
            logs = logs,
            start_date = habit.created_at,
            target_minutes = habit.target_minutes if hasattr(habit, "target_minutes") else 30
        )

        habit_data.append({
            "habit": habit,
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "today_done": today_done,
        })

    return render(request, "tracker/index.html", {
        "habit_data": habit_data,
    })


@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, users=request.user)

    if request.user != habit.owner and request.user not in habit.users.all():
        return HttpResponseForbidden("You do not have access to this habit")


    selected_user_id = request.GET.get("user", request.user.id)
    selected_user = get_object_or_404(User, id=selected_user_id)

    logs = HabitLog.objects.filter(habit=habit, user=selected_user).order_by('-date')
    today_done = logs.filter(date=date.today()).exists()
    streak_data = get_streaks_and_progress(selected_user, habit) or {
        "current_streak": 0,
        "longest_streak": 0,
        "completion_percent": 0,
    }

    if request.method == 'POST' and selected_user == request.user:
        form = HabitLogForm(request.POST)
        if form.is_valid():
            note = form.cleaned_data['note']
            minutes_done = form.cleaned_data["minutes_done"]
            HabitLog.objects.update_or_create(
                habit=habit,
                user=request.user,
                date=date.today(), 
                defaults={
                    'note': note,
                    "minutes_done": minutes_done,
                })
            return redirect('habit_detail', habit_id=habit.id)
    else:
        if selected_user == request.user:
            try:
                log_today = HabitLog.objects.get(user=request.user, habit=habit, date=date.today())
                minutes_done = log_today.minutes_done
                note = log_today.note
            except HabitLog.DoesNotExist:
                note = ""
                minutes_done = None
            form = HabitLogForm(initial={
            "note": note,
            "minutes_done": minutes_done,
            })
        else:
            form = None

    all_users = [habit.owner] + list(habit.users.all())
    everyone_progress = []

    for user in all_users:
        logs_for_user = HabitLog.objects.filter(habit=habit, user=user)
        streak = get_streaks_and_progress(user, habit) or {
            "current_streak": 0,
            "longest_streak": 0,
            "completion_percent": 0,
        }
        today_done = logs_for_user.filter(date=date.today()).exists()

        everyone_progress.append({
            "user": user,
            "current_streak": streak["current_streak"],
            "longest_streak": streak["longest_streak"],
            "completion_percent": streak["completion_percent"],
            "today_done": today_done,
        })

    return render(request, 'tracker/habit_detail.html', {
        "habit": habit,
        "logs": logs,
        "today_done": today_done,
        "form": form,
        "streak": streak_data,
        "shared_users": habit.users.exclude(id=request.user.id),
        "selected_user": selected_user,
        "everyone_progress": everyone_progress,
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
    logs = HabitLog.objects.filter(user=user, habit=habit)
    start_date = habit.created_at
    target_minutes = habit.target_minutes 

    streak_data = calculate_streaks(logs, start_date, target_minutes)
@login_required
def friends_list(request):
    user = request.user
    friends = user.friends.all()
    incoming_requests = FriendRequest.objects.filter(to_user=user)
    return render(request, "tracker/friends_list.html", {
        "friends": friends,
        "incoming_requests": incoming_requests,
    })

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        pass
    else:
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    
    return redirect("search_users")

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    from_user = friend_request.from_user

    request.user.friends.add(from_user)
    from_user.friends.add(request.user)

    friend_request.delete()

    return redirect('friends_list')

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