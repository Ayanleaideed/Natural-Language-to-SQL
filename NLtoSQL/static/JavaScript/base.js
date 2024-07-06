document.addEventListener('DOMContentLoaded', (event) => {
  const body = document.body;
  const themeToggle = document.getElementById('theme-toggle');
  const userProfile = document.getElementById('userProfile');
  const userIcon = document.getElementById('userIcon');

  // Check local storage for theme
  const currentTheme = localStorage.getItem('theme') || 'light-mode';
  body.classList.add(currentTheme);

  // Update icon based on current theme
  themeToggle.className = currentTheme === 'dark-mode' ? 'fas fa-sun' : 'fas fa-moon';

  themeToggle.addEventListener('click', () => {
    if (body.classList.contains('light-mode')) {
      body.classList.replace('light-mode', 'dark-mode');
      themeToggle.className = 'fas fa-sun';
      localStorage.setItem('theme', 'dark-mode');
    } else {
      body.classList.replace('dark-mode', 'light-mode');
      themeToggle.className = 'fas fa-moon';
      localStorage.setItem('theme', 'light-mode');
    }
  });

  // Toggle the visibility of userProfile div
  userIcon.addEventListener('click', function() {
    if (userProfile.style.display === 'none' || userProfile.style.display === '') {
      userProfile.style.display = 'block';
    } else {
      userProfile.style.display = 'none';
    }
  });
});
