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

  // Store the current tab in localStorage
  localStorage.setItem('currentTab', tabName);
}

// Function to load the default or previously clicked tab
function loadTab() {
  var currentTab = localStorage.getItem('currentTab');
  if (currentTab) {
    document.querySelector(`.tab-button[onclick="openTab(event, '${currentTab}')"]`).click();
  } else {
    // Set default tab
    document.getElementsByClassName("tab-button")[0].click();
  }
}

// Load the tab when the page loads
window.onload = loadTab;


function adjustRows(textarea) {
  // Only adjust the height if there's content
  if (textarea.value.trim() !== "") {
    textarea.style.height = '96px'; // Reset height
    textarea.style.height = (textarea.scrollHeight) + 'px';
  }
}


function indentOnTab(event) {
  if (event.key === 'Tab') { // Check if the pressed key is the Tab key
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

function updateDatabaseInfo() {
  var sqlSelect = document.getElementById('selected_database_sql');
  var nlSelect = document.getElementById('selected_database_nl');

  // Determine which dropdown triggered the change
  var selectedOption = document.activeElement.id === 'selected_database_sql' ? sqlSelect.options[sqlSelect.selectedIndex] : nlSelect.options[nlSelect.selectedIndex];

  if (selectedOption) {
    var dbSize = selectedOption.getAttribute('data-size');
    var dbName = selectedOption.getAttribute('data-name');
    var dbUser = selectedOption.getAttribute('data-user');
    var dbType = selectedOption.getAttribute('data-type');
    var dbHost = selectedOption.getAttribute('data-host');

    document.getElementById('db-size').textContent = dbSize;
    document.getElementById('db-name').textContent = dbName;
    document.getElementById('db-user').textContent = dbUser;
    document.getElementById('db-type').textContent = dbType;
    document.getElementById('db-host').textContent = dbHost;
  } else {
    console.log('No option selected');
  }
}

// Initialize the right panel with the first database info if available
document.addEventListener('DOMContentLoaded', function() {
  updateDatabaseInfo();

  // Add event listeners for both dropdowns
  document.getElementById('selected_database_sql').addEventListener('change', updateDatabaseInfo);
  document.getElementById('selected_database_nl').addEventListener('change', updateDatabaseInfo);
});


function handleBindQuery() {
  document.querySelectorAll('.query-entry').forEach(item => {
      item.onclick = function() {
          document.getElementById('sql-input').value = this.textContent.trim();
          document.getElementById('nl-input').value = this.textContent.trim();
      }
  });
}

document.addEventListener('DOMContentLoaded', handleBindQuery);










