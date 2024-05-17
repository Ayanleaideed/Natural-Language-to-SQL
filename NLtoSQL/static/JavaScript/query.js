function openTab(evt, tabName) {
  var i, tabcontent, tabbuttons;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tabbuttons = document.getElementsByClassName("tab-button");
  for (i = 0; i < tabbuttons.length; i++) {
    tabbuttons[i].className = tabbuttons[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

// Set default tab
document.getElementsByClassName("tab-button")[0].click();

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
  textarea.addEventListener('input', () => adjustRows(textarea)); // Adjust rows on input
});
