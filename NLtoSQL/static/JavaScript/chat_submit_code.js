function updateCodeSnippet(code) {
  const codeSnippet = document.getElementById('response-output');
  codeSnippet.textContent = code;
}

function copyToClipboard() {
  const copyText = document.getElementById('response-output').textContent;
  navigator.clipboard.writeText(copyText).then(() => {
      showMessage('Copied to clipboard!', 'success');
  }).catch(err => {
      showMessage('Failed to copy. Please try again.', 'error');
      console.error('Failed to copy: ', err);
  });
}

function showMessage(text, type) {
  const messageContainer = document.getElementById('message-container');
  const message = document.getElementById('message');
  const messageText = document.getElementById('message-text');

  messageText.textContent = text;
  message.className = `message message-${type}`;
  messageContainer.style.display = 'block';
}

function closeMessage() {
  document.getElementById('message-container').style.display = 'none';
}