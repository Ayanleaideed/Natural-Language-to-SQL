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
// Loading functions
function startLoading() {
  document.getElementById('mainContent').classList.add('loading');
}

function stopLoading() {
  document.getElementById('mainContent').classList.remove('loading');
}

document.addEventListener('DOMContentLoaded', () => {
  const loaderContainer = document.querySelector('.loader-container');
  const blurOverlay = document.querySelector('.blur-overlay');
  const mainContent = document.querySelector('main');

  function showLoader() {
    loaderContainer.style.display = 'flex'; // Show loader
    blurOverlay.classList.add('active');
    mainContent.classList.add('blur');
  }

  function hideLoader() {
    loaderContainer.style.display = 'none'; // Hide loader
    blurOverlay.classList.remove('active');
    mainContent.classList.remove('blur');
  }

  // Handle internal link clicks
  document.querySelectorAll('a[href^="/"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      showLoader();
      setTimeout(() => {
        window.location.href = link.href;
      }, 100); 
    });
  });

  // Show loader immediately when the script runs
  showLoader();

  // Set a timeout to hide the loader after 15 seconds
  setTimeout(hideLoader, 15000);

  // Still listen for the load event to potentially hide the loader earlier
  window.addEventListener('load', () => {
    if (performance.now() < 15000) {
      hideLoader();
    }
  });
});