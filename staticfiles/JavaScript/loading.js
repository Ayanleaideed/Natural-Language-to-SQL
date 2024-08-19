
  document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelectorAll('.hero-messages h1');
    const ctaButton = document.querySelector('.cta-button');
    const urls = [
      "/generate",
      "/query",
      "/management"
    ];
    let currentMessageIndex = 0;

    function showNextMessage() {
      messages[currentMessageIndex].classList.remove('active');
      currentMessageIndex = (currentMessageIndex + 1) % messages.length;
      messages[currentMessageIndex].classList.add('active');
      ctaButton.href = urls[currentMessageIndex];
    }

    setInterval(showNextMessage, 3000);

    // Show the first message initially
    messages[currentMessageIndex].classList.add('active');
    ctaButton.href = urls[currentMessageIndex];
  });

