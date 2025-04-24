document.addEventListener("DOMContentLoaded", function () {
    const markDoneButtons = document.querySelectorAll('.mark-done-btn');
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    if (!csrfToken) {
        console.error("CSRF token not found");
        return; 
    }

    markDoneButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const habitId = e.target.getAttribute('data-habit-id');
            if (!habitId) {
                console.error('No habit ID found');
                return;
            }

            fetch(`/habit/${habitId}/mark_done/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ habitId })
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log("Habit marked as done");
                const completionText = document.getElementById('completion');
                if (completionText) {
                    completionText.textContent = "100";
                }
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar) {
                    progressBar.style.width = '100%';
                    progressBar.setAttribute('aria-valuenow', '100');
                }
                const todayStatus = document.querySelector(`.today-status[data-habit-id="${habitId}"]`);
                if (todayStatus) {
                    todayStatus.innerHTML = "✅";
                }

                markDoneButtons.textContent = "Done!";
                markDoneButtons.disabled = true;
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    });
});
