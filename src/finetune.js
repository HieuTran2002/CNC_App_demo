const tableBody = document.querySelector("#dynamicTable tbody");
const addRowButton = document.getElementById("addRowBtn");

function requestImage() {
    socket.emit('request_image', { id: 'result1', path:'src/pics/loyd2.jpg' });
}

socket.on("table/add_row", (data) => {
    const rowHTML = `
        <tr class="bg-white border-b border-gray-700">
        <td class="px-3 py-1">${data.id}</td>
        ${data.columns.map((cell, index) => `
            <td class="px-6 py-1">
            <div contenteditable="true" 
            class="editable-cell focus:outline-none focus:ring-2 focus:ring-blue-500">
            ${cell}
            </div>
            </td>`).join("")}
        <td class="px-6 py-1">
        <div class="flex justify-center items-center">
        <input id="checkbox-${data.id}" type="checkbox" value="" 
    class="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded" 
    onclick="toggleHighlight(this)">
        </div>
        </td>
        </tr>`;
    tableBody.innerHTML += rowHTML;
});

function toggleHighlight(checkbox) {
    // Function to toggle highlight class
    const row = checkbox.closest("tr"); // Get the parent row of the checkbox
    if (checkbox.checked) {
        row.classList.add("bg-green-100"); // Add highlight class
    } else {
        row.classList.remove("bg-green-100"); // Remove highlight class
    }
}

// Enable/Disable user interaction
socket.on("table/control", (data) => {
    if (data['isEnable'] == '0') {
        tableBody.style.pointerEvents = "none";
    }
    else if (data['isEnable'] == '1') {
        tableBody.style.pointerEvents = "auto";
    }
});

// Example toggleHighlight function
function toggleHighlight(checkbox) {
    const row = checkbox.closest("tr");
    console.log("highlight")
    row.classList.toggle("bg-green-200", checkbox.checked);
}

window.onload = function() {
    console.log("request image")
    socket.emit("table/random_row");
    requestImage();
};

