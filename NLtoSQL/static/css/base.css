/* Reset and basic styles */
body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
}

/* Light Mode */
body.light-mode {
  background-color: #f4f4f4;
  color: #000;
}

/* Dark Mode */
body.dark-mode {
  background-color: #121212;
  color: black;
}


/* Main content area styles */
main {
  flex: 1 0 auto;
  padding: 2rem;
  margin-top: 45px;
  overflow-y: auto;
}

/* Animation for content loading */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Apply animation to the content block */
main > * {
  animation: fadeInUp 0.5s ease-out;
}

/* Ensure smooth scrolling for the entire page */
html {
  scroll-behavior: smooth;
}

/* Optional: Add a transition for smoother content changes */
main {
  transition: opacity 0.3s ease;
}

/* Optional: Style for when content is loading */
main.loading {
  opacity: 0.3;
}

/* Footer */
footer {
  background-color: #343a40;
  color: #fff;
  text-align: center;
  padding: 0.2rem;
  position: relative;
  bottom: 0;
}
/* Navbar */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 0.5rem 1rem;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.3));
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #4a148c;
  font-size: 1.22rem;
  font-weight: bold;
  font-family: Arial, sans-serif !important;
  transition: color 0.3s ease-in-out;
}

.logo-image {
  height: 32px;
  margin-right: 0.5rem;
}

.logo:hover {
  color: #7e57c2; /* Change color on hover */
}

/* Navigation Links */
.nav-actions {
  display: flex;
  border-radius: 99px;
  padding: 0.25rem;
  backdrop-filter: blur(10px);
  background-color: #ffffffbf;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  gap: 20px;
  padding: 6px;
}

.nav-link {
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-family: Arial, sans-serif !important;
  color: hsla(0, 0%, 0%, 0.622);
  font-weight: bold;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.nav-link:hover {
  background-color: hwb(235 10% 36% / 0.813);
  color: #ffffff;
  transform: scale(1.05); /* Slightly enlarge on hover */
}

/* User Actions */
.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 9999px;
  padding: 0.35rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s ease;
}

.user-actions:hover {
  background-color: rgba(255, 255, 255, 0.7); /* Slightly lighter on hover */
}

/* Auth Buttons */
.auth-button {
  background-color: rgba(255, 255, 255, 0.5);
  color: #4a148c;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  text-decoration: none;
  transition: background-color 0.3s ease, color 0.3s ease;
  font-size: 0.875rem;
}

.auth-button.highlight {
  background-color: #7e57c2;
  color: white;
}

.auth-button:hover {
  background-color: #6c4f9c;
  color: #ffffff;
}


.auth-button:hover {
  background-color: rgba(124, 150, 255, 0.8);
}

.auth-button.highlight:hover {
  background-color: #6a1b9a;
}

/* Ensure the main content starts below the navbar */
body {
  padding-top: 60px; /* Adjust this value based on your navbar height */
}

/* Additional styles for responsiveness */
@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-actions, .user-actions {
    margin-top: 1rem;
  }
}

.username {
  color: #4B0082;
  font-size: 14px;
  font-weight: bold;
  margin-left: 10px;
}


/* Custom Alerts */
.custom-alerts {
  margin-top: 5%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;

}

.custom-alert {
  padding: 15px;
  margin-bottom: 5px;
  border-radius: 5px;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  max-width: 800px;
}

.custom-alert-warning {
  background-color: #ffcc00;
  color: #333;
}

.custom-alert-info {
  background-color: #d9edf7;
  color: #31708f;
}

.custom-alert-success {
  background-color: #dff0d8;
  color: #3c763d;
}

.custom-alert-error {
  background-color: #ff0000;
  color: white;
  text-transform: capitalize;
  font-weight: bold;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: inherit;
  position: absolute;
  right: 10px;
}

/* User Profile Settings */
.userProfile-settings {
  display: none;
  position: absolute;
  right: 15%;
  margin-top: 10px;
  background-color: hsl(202, 100%, 45%);
  width: 300px;
  text-align: center;
  color: white;
  font-weight: bolder;
  font-family: monospace;
  border-radius: 5px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
  padding: 10px;
  z-index: 1000;
}

.userProfile-settings.active {
  display: block;
}

.userProfile-settings {
  animation: slideDown 0.3s ease-in-out forwards;
}

@keyframes slideDown {
  from {
    top: 6%;
    opacity: 0.5;
  }
  to {
    top: 6.5%;
    opacity: 1;
  }
}

/* Wrapper */
.wrapper {
  background-color: hsla(240, 33%, 26%, 0.39);
  border-radius: 15px;
  padding: 10px;
  box-shadow: 0px 0px 10px rgba(224, 248, 255, 0.719);
}


/* Loader and Overlay Styles */
.blur-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* Dark overlay */
  backdrop-filter: blur(8px); /* Enhanced blur effect */
  z-index: 9998; /* Behind the loader */
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.blur-overlay.active {
  opacity: 1;
  visibility: visible;
}

.loader-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999; /* Above the blur overlay */
  display: none; /* Hidden by default */
}

/* Loader Animation */
#page {
  display: flex;
  justify-content: center;
  align-items: center;
}

#container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

#h3 {
  color: white;
  font-family: Arial, sans-serif;
  font-size: 16px;
}

.ring {
  width: 190px;
  height: 190px;
  border: 1px solid transparent;
  border-radius: 50%;
  position: absolute;
}

.ring:nth-child(1) {
  border-bottom: 8px solid rgb(255, 141, 249);
  animation: rotate1 2s linear infinite;
}

@keyframes rotate1 {
  from {
    transform: rotateX(50deg) rotateZ(110deg);
  }
  to {
    transform: rotateX(50deg) rotateZ(470deg);
  }
}

.ring:nth-child(2) {
  border-bottom: 8px solid rgb(255, 65, 106);
  animation: rotate2 2s linear infinite;
}

@keyframes rotate2 {
  from {
    transform: rotateX(20deg) rotateY(50deg) rotateZ(20deg);
  }
  to {
    transform: rotateX(20deg) rotateY(50deg) rotateZ(380deg);
  }
}

.ring:nth-child(3) {
  border-bottom: 8px solid rgb(0, 255, 255);
  animation: rotate3 2s linear infinite;
}

@keyframes rotate3 {
  from {
    transform: rotateX(40deg) rotateY(130deg) rotateZ(450deg);
  }
  to {
    transform: rotateX(40deg) rotateY(130deg) rotateZ(90deg);
  }
}

.ring:nth-child(4) {
  border-bottom: 8px solid rgb(252, 183, 55);
  animation: rotate4 2s linear infinite;
}

@keyframes rotate4 {
  from {
    transform: rotateX(70deg) rotateZ(270deg);
  }
  to {
    transform: rotateX(70deg) rotateZ(630deg);
  }
}

/* Main Content Blur */
main.blur {
  filter: blur(8px);
}

