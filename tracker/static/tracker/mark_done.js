document.addEventListener("DOMContentLoaded", function () {
    const markDoneButtons = document.querySelectorAll('.mark-done-btn');

    markDoneButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const habitId = e.target.getAttribute('data-habit-id');
            if (habitId) {
                fetch(`/mark_done/${habitId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({ habitId })
                })
                .then(response => response.json())
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
