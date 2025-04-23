from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.db.models import Q, Sum
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from itertools import groupby
from operator import attrgetter

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
        today_minutes = logs.filter(date=date.today()).aggregate(Sum("minutes_done"))["minutes_done__sum"] or 0
    
        today_done = today_minutes >= habit.target_minutes

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

@require_POST
@login_required
def mark_habit_done(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, users=request.user)
    HabitLog.objects.create(
        habit=habit,
        user=request.user,
        date=date.today(),
        minutes_done=habit.target_minutes,
        note="Marked done via button"
    )
    
    return JsonResponse({"status": "success", "message": "Habit marked as done!"})
    print(f"Returning response for habit {habit_id}...")
    return JsonResponse({'status': 'success'})



@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, users=request.user)

    if request.user != habit.owner and request.user not in habit.users.all():
        return HttpResponseForbidden("You do not have access to this habit")

    selected_user_id = request.GET.get("user", request.user.id)
    selected_user = get_object_or_404(User, id=selected_user_id)

    logs = HabitLog.objects.filter(habit=habit, user=selected_user).order_by('-date')

    today_minutes = logs.filter(date=date.today()).aggregate(Sum("minutes_done"))["minutes_done__sum"] or 0
    today_done = today_minutes >= habit.target_minutes

    today_completion = round((today_minutes / habit.target_minutes) * 100, 1) if habit.target_minutes else 0

    streak_data = get_streaks_and_progress(selected_user, habit) or {
        "current_streak": 0,
        "longest_streak": 0,
        "completion_percent": 0,
    }

    if request.method == 'POST':
        if selected_user == request.user:
            form = HabitLogForm(request.POST)
            if form.is_valid():
                note = form.cleaned_data['note']
                minutes_done = form.cleaned_data["minutes_done"]

                total_today = HabitLog.objects.filter(
                    habit=habit,
                    user=request.user, 
                    date=date.today(),
                ).aggregate(Sum("minutes_done"))["minutes_done__sum"] or 0

                if minutes_done < 1:
                    form.add_error("minutes_done", "Minutes must be positive")
                elif minutes_done + total_today < total_today:
                    form.add_error("minutes done", f"You have already logged {total_today} minutes today.")
                else:
                    HabitLog.objects.create(
                        habit=habit,
                        user=request.user,
                        date=date.today(), 
                        note=note,
                        minutes_done=minutes_done,
                    )
                return redirect('habit_detail', habit_id=habit.id)
            else:
                form = None
    else:
        if request.user == selected_user:
            form = HabitLogForm()
        else:
            form = None

    logs_by_date = []
    for date_value, group in groupby(logs, key=attrgetter("date")):
        logs_by_date.append({
            "date": date_value,
            "logs": list(group),
        })

    for entry in logs_by_date:
        total = sum(log.minutes_done for log in entry['logs'])
        entry['total_minutes'] = total

    all_users = [habit.owner] + list(habit.users.all())
    all_users = [user for user in all_users if user is not None]
    everyone_progress = []

    for user in all_users:
        logs_for_user = HabitLog.objects.filter(habit=habit, user=user)
        streak = get_streaks_and_progress(user, habit) or {
            "current_streak": 0,
            "longest_streak": 0,
            "completion_percent": 0,
        }

        user_today_minutes = HabitLog.objects.filter(
            habit=habit,
            user=user,
            date=date.today(),
        ).aggregate(Sum('minutes_done'))['minutes_done__sum'] or 0

        today_done = user_today_minutes >= habit.target_minutes    

        everyone_progress.append({
            "user": user,
            "current_streak": streak["current_streak"],
            "longest_streak": streak["longest_streak"],
            "completion_percent": streak["completion_percent"],
            "today_done": today_done,
        })        

    return render(request, 'tracker/habit_detail.html', {
        "habit": habit,
        "logs_by_date": logs_by_date,
        "today_minutes": today_minutes,
        "today_done": today_done,
        "form": form,
        "today_completion": today_completion,
        "streak": streak_data,
        "shared_users": habit.users.exclude(id=habit.owner.id) if habit.owner else habit.users.all(),
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
            habit.owner = request.user
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
    return streak_data

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

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)

    habits = Habit.objects.filter(Q(owner=profile_user) | Q(users=profile_user)).distinct()

    already_requested = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).exists()
    already_friends = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=profile_user) |
        Q(from_user=profile_user, to_user=request.user),
        is_accepted = True
    ).exists()

    can_send_request = (
        profile_user != request.user and not already_requested and not already_friends
    )

    if request.method == 'POST' and "send_friend_request" in request.POST and can_send_request:
        FriendRequest.objects.create(from_user=request.user, to_user=profile_user)
        return redirect("profile_view", username=username)

    habit_data = []
    for habit in habits:
        shared_with = habit.users.exclude(id=profile_user.id)
        habit_data.append({
            "habit": habit,
            "is_owner": habit.owner == profile_user,
            "shared_with": shared_with,
        })

    return render(request, "tracker/profile.html", {
        "profile_user": profile_user,
        "habits": habit_data,
        "can_send_request": can_send_request,
        "already_requested": already_requested,
        "already_friends": already_friends,
    })

@login_required
def shared_habits_view(request):
    shared_habits = Habit.objects.filter(users=request.user)
    shared_habits = [habit for habit in shared_habits if habit.users.count() > 1]
    return render(request, "tracker/shared_habits.html", {
        "habits": shared_habits,
    })