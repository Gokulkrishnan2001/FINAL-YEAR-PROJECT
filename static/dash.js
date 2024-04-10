const sideMenu = document.querySelector('aside');
const menuBtn = document.getElementById('menu-btn');
const closeBtn = document.getElementById('close-btn');
const darkMode = document.querySelector('.dark-mode');

// Function to toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode-variables');
    darkMode.querySelector('span:nth-child(1)').classList.toggle('active');
    darkMode.querySelector('span:nth-child(2)').classList.toggle('active');

    // Store the theme preference in local storage
    const isDarkMode = document.body.classList.contains('dark-mode-variables');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
}

// Function to apply the stored theme preference
function applyStoredThemePreference() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
        toggleDarkMode(); // Apply dark mode if stored preference is dark
    }
}

// Event listeners
menuBtn.addEventListener('click', () => {
    sideMenu.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    sideMenu.style.display = 'none';
});

darkMode.addEventListener('click', toggleDarkMode);


// Apply stored theme preference when the page loads
window.addEventListener('load', applyStoredThemePreference);


// Get the canvas element
var ctx = document.getElementById('expenditureChart').getContext('2d');
var categoryLabels = ['Feed', 'Veterinary', 'Equipment', 'Labor'];
var categoryAmounts = [1250, 7500, 27000, 24300]
// Create the pie chart
var expenditureChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: categoryLabels, // Array of category labels
        datasets: [{
            label: 'Expenditure by Category',
            data: categoryAmounts, // Array of category amounts
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)', // Red
                'rgba(54, 162, 235, 0.6)', // Blue
                'rgba(255, 206, 86, 0.6)', // Yellow
                'rgba(75, 192, 192, 0.6)', // Green
                // Add more colors as needed
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Expenditure by Category'
        }
    }
});
