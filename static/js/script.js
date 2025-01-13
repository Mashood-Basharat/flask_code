document.addEventListener("DOMContentLoaded", function() {
    const toggleIcon = document.querySelector(".toggle-icon");
    const navLinks = document.querySelector(".nav-link");

    toggleIcon.addEventListener("click", () => {
        navLinks.classList.toggle("show-menu");
    });

});


// JavaScript to handle dropdowns if any additional functionality is needed
document.getElementById('appUsageLink').addEventListener('click', function(event) {
    event.preventDefault(); // Prevents page jump
    document.getElementById('appUsageContent').classList.toggle('show');
});

document.getElementById('documentationLink').addEventListener('click', function(event) {
    event.preventDefault(); // Prevents page jump
    document.getElementById('documentationContent').classList.toggle('show');
});



document.getElementById("setup-btn").addEventListener("click", function() {
    alert("SyncKing-Kong setup initiated.");
    // Call backend API to start setup
});

document.getElementById("process-btn").addEventListener("click", function() {
    const videoFile = document.getElementById("video-file").value;
    const vocalFile = document.getElementById("vocal-file").value;
    const quality = document.getElementById("quality").value;

    if (videoFile) {
        alert(`Processing started for video: ${videoFile} with quality: ${quality}`);
        // Call backend API to process inputs
    } else {
        alert("Please provide a video file.");
    }
});

document.getElementById("download-btn").addEventListener("click", function() {
    // Call backend API to trigger video download
    alert("Downloading processed video...");
});

// Handles the progress bar functionality
function update() {
    // Prevent immediate form submission
    const form = document.getElementById("uploadForm");

    // Make the progress bar visible
    document.getElementById("Progress_Status").style.display = "block";

    let element = document.getElementById("myprogressBar");
    let width = 2; // Start with 2% progress
    const interval = 100; // Slower progress interval
    const identity = setInterval(scene, interval);

    function scene() {
        if (width >= 100) {
            clearInterval(identity);
            // Submit the form programmatically after progress is complete
            form.submit();
        } else {
            width += 2; // Increment progress
            element.style.width = width + '%';
        }
    }
}