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