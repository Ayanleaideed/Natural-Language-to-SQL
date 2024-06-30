const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');

    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-mode');
      const isDarkMode = body.classList.contains('dark-mode');
      themeToggle.classList.toggle('fa-moon', !isDarkMode);
      themeToggle.classList.toggle('fa-sun', isDarkMode);
      themeToggle.style.color = isDarkMode ? '#ffffff' : '#ffc107';
      body.style.backgroundColor = isDarkMode ? 'black' : '#ffffff';
      body.style.color = isDarkMode ? 'black' : 'black';

    });


    // Get references to the elements
const userProfile = document.getElementById('userProfile');
const userIcon = document.getElementById('userIcon');

// Add click event listener to the icon
userIcon.addEventListener('click', function() {
    // Toggle the visibility of userProfile div
    if (userProfile.style.display === 'none') {
        userProfile.style.display = 'block';
    } else {
        userProfile.style.display = 'none';
    }
});
