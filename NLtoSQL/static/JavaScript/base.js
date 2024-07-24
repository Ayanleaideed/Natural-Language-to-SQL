document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const themeToggle = document.getElementById('theme-toggle');
  const userProfile = document.getElementById('userProfile');
  const userIcon = document.getElementById('userIcon');

  // Function to apply theme
  const applyTheme = (theme) => {
    body.classList.remove('light-mode', 'dark-mode');
    body.classList.add(theme);
    themeToggle.className = theme === 'dark-mode' ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('theme', theme);
  };

  // Check local storage for theme
  const currentTheme = localStorage.getItem('theme') || 'light-mode';
  applyTheme(currentTheme);

  // Toggle theme on button click
  themeToggle.addEventListener('click', () => {
    const newTheme = body.classList.contains('light-mode') ? 'dark-mode' : 'light-mode';
    applyTheme(newTheme);
  });

  // Toggle the visibility of userProfile div
  userIcon.addEventListener('click', () => {
    userProfile.style.display = userProfile.style.display === 'block' ? 'none' : 'block';
  });
});

// Loading functions
function startLoading() {
  document.getElementById('mainContent').classList.add('loading');
}

function stopLoading() {
  document.getElementById('mainContent').classList.remove('loading');
}
