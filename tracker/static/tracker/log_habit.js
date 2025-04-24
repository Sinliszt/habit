document.addEventListener('DOMContentLoaded', () => {

    event.preventDefault();
    document.querySelector("#log-button").addEventListener('click', () => {
        const csrfToken = '{{ csrf_token }}'
        fetch("{% url 'log_shared_habit %}", {
            method: 'POST',
            headers: {
                "X-CSRFToken": csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        body: `habit_id={{ habit.id }}&note=Shared logging via JS!`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status == "success") {
                document.getElementById("status-msg").innerText = `Logged by ${data.user} on ${data.today}`;
            } else {
                document.getElementById("status-msg").innerText = data.message;
            }
        })
    });
});