document.addEventListener('DOMContentLoaded', () => {
    const heatmapContainer = document.getElementById("calendar-heatmap");
    const habitId = window.location.pathname.split("/")[2];

    function calculateCompletion(minutesDone, targetMinutes) {
        return targetMinutes ? (minutesDone / targetMinutes) * 100: 0;
    }

    function getColor(percent) {
        if (percent === 0) return "#ebedf0";
        if (percent < 25) return "#c6e48b";
        if( percent < 50) return "#7bc96f";
        if(percent < 75) return "#239a3b";
        return "#196127";
    }

    const today = new Date();
    const startDate = new Date(today.getFullYear(), 0, 1);
    const endDate = new Date(today.getFullYear(), 11, 31);

    const todayStr = today.toISOString().split("T")[0];

    function renderHeatmap(data, container) {

        container.innerHTML = "";

        for(let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
            const dateStr = d.toISOString().split("T")[0];
            const dayData = data[dateStr] || {minutesDone : 0, targetMinutes : 0};

            const percent = calculateCompletion(dayData.minutesDone, dayData.targetMinutes);

            const cell = document.createElement("div");
            cell.className = "heatmap-cell";
            cell.title = `${dateStr}: ${percent}% completed`;

            if (dateStr > todayStr) {
                cell.style.backgroundColor = "#d0d0d0";
            } else {
                cell.style.backgroundColor = getColor(percent);
            }

            container.appendChild(cell);
        }
    }
    
    fetch(`/habit/${habitId}/log-data`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            renderHeatmap(data, heatmapContainer);
        });


});