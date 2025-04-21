document.addEventListener('DOMContentLoaded', () => {
    function updateCompletion(newPercent) {
        document.getElementById("completion").innerText = newPercent;
        const bar = document.querySelector(".progress-bar");
        bar.style.width = newPercent + "%";
        bar.setAttribute("aria-valuenow", newPercent);
    }
})