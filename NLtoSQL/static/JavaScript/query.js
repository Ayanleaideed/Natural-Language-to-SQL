function adjustRows(textarea) {
  const lines = textarea.value.split('\n');
  const totalLines = lines.length + 1; // +1 to always maintain one row ahead
  textarea.rows = totalLines;
}

function indentOnTab(event) {
  if (event.keyCode === 9) { // Check if the pressed key is the Tab key (key code 9)
      event.preventDefault(); // Prevent the default Tab key behavior

      // Get the current selection and caret position
      const textarea = event.target;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      // Insert two spaces at the caret position
      const currentText = textarea.value;
      const newText = currentText.substring(0, start) + '  ' + currentText.substring(end);

      // Update the textarea's value and caret position
      textarea.value = newText;
      textarea.setSelectionRange(start + 2, start + 2);
  }
}

document.querySelectorAll('textarea').forEach(textarea => {
  textarea.addEventListener('keydown', indentOnTab);
});