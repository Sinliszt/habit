Habit is a web application that helps users build consistent and productive habits by allowing them to log their habits daily, set personalised goals, and collaborative tracking. Users can set up habits (e.g. “Read 30 minutes daily”), log their progress by number of minutes, view completion analytics through heatmaps and streaks and optionally share their habits with friends. Friends can view each other's shared habits, track mutual progress.

# Distinctiveness and Complexity

The project is significantly different in both concept and implementation from other projects in CS50W. While it does include minimal social features like friend requests, the primary focus of that is to be able to share activity and time-based behavioural tracking, data driven insights. It does not have “content feeds” or a “bidding system”. Users do not have direct interactions with others like in commenting or bidding.
The app is fully mobile-responsive, using Bootstrap to be able to display across a range of devices. Access control is strictly enforced on shared views to ensure privacy and security, and AJAX functionality ensures smooth and reload-free interactions.

In terms of complexity, it is in how the habits are modeled, tracked and visualized:

- **Time-based logging and analytics: **Unlike static data entries or one-off transactions, habits are reset and can be logged daily, with durations and notes. Each log contributes to the streak calculations, completion percentages and progress evaluations
- **Shared Habits: **Habits can be shared with selected friends for collaborative tracking without giving up personal ownership or data integrity. Users only see habits they’ve been granted access to.
- **Progress Visualisation: **the frontend integrates a custom-built calendar using JS and AJAX, to show daily completion percentages through colour intensity. This updates in real time as logs are entered.
- **Marking Habits: **Users can mark habits as “done” from the dashboard without reloading the page. And the requests are used to asynchronously update data and refresh visual components like the progress bar and completion stats.

## File Structure

### Core Django App: **habit/**

- **models.py**
  - _User:_  Extends AbstractUser with symmetric friends relationship
  - _Category:_ Habit categories (Mindfulness, Fitness etc.)
  - _Habit:_ Main model with name, description, target time, category, creator, and optional shared users
  - _HabitLog:_ Stores daily progress like the data, minutes done, note, completion status
  - _FriendRequest:_ Manages friend requests, with sender, receiver, timestamp and acceptance status
- **forms.py**
  - _HabitForm:_ For creating habits, with dynamic filtering for friends
  - _HabitLogForm:_ For logging time and optional notes. It is alos customised with widgets for better UI
- **utils.py**
  - Contains the logic to calculate habit analytics like current streak, longest streak, and completion. This is used across views and visualisations
- **views.py**
  - Handles user login/logout/signup, dashboard display, habit creation, habit details, logging, calendar heatmap data, friend request handling and profiles
- **urls.py**
  - Maps URLs to view functions

### Static Files

- **mark_done.js**
  - Handles AJAX requests to mark a habit as completed and updated progress without reloading the page
- **calendar_heatmap.js**
  - Renders a dynamic heatmap calendar using data fetched via AJAX, indicating completion levels per day across a whole year
- **styles.css**
  - Styles the heat map layout

### Templates

- _layout.html_: Base layout for all pages with navigation at the top
- _index.html_: Main dashboard showing overview of habits, streaks, and today’s progress
- _create_habit.html_: Contains the form for  creating new habits with all the required fields
- _habit_detail.html_: Displays detailed habit information, logs (based on user selected), streaks, and user-specific analytics
- _profile.html_: Shows user profile with habits and whether they own that habit and who it is shared with. Users can also send friend requests here
- _friends_list.html_: Shows friend requests and friends
- _friend_search.html_: Users can search for people to add as friends or view profiles
- _shared_habits.html_: displays habits that the user has shared, or has been added to
- _signup.html / login.html_: Standard authentication templates

## Running the Application

**Requirements**
- Python 3.8+
- pip
- Django
- Virtual environment tools (venv)
- All dependencies listed in requirements.txt

### Steps to run

- Clone the repository to local machine
- Open the habit directory
- Set up virtual environment
- Install dependencies using pip
- Apply migrations
- Create superuser if you need to access the admin panel
- Run the server
