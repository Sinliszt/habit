document.addEventListener("DOMContentLoaded", function () {
    const markDoneButtons = document.querySelectorAll('.mark-done-btn');
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfTokenElement) {
        console.error("CSRF token not found! Make sure it's in the HTML.");
        return; 
    }   
    const csrfToken = csrfTokenElement.value;

    markDoneButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const habitId = e.target.getAttribute('data-habit-id');
            if (habitId) {
                fetch(`/habit/${habitId}/mark_done/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ habitId })
                })
                .then(response => {
                    if(!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        });
                    }
                    return response.json()
                })
                .then(data => {
                    console.log('Success:', data);
                    e.target.textContent = "Done!";
                    e.target.disabled = true;
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            } else {
                console.error('No habit ID found!');
            }
        });
    });
});
