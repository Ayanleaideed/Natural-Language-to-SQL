function openTab(evt, tabName) {
  var i, tabcontent, tabbuttons;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tabbuttons = document.getElementsByClassName("tab-button");
  for (i = 0; i < tabbuttons.length; i++) {
    tabbuttons[i].classList.remove("active");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");

  // Store the current tab in localStorage
  localStorage.setItem('currentTab', tabName);
}

// Function to load the default or previously clicked tab
function loadTab() {
  var currentTab = localStorage.getItem('currentTab');
  if (currentTab) {
    var tabButton = document.querySelector(`.tab-button[data-tab="${currentTab}"]`);
    if (tabButton) {
      tabButton.click();
    } else {
      // Set default tab if stored tab doesn't exist
      document.querySelector('.tab-button').click();
    }
  } else {
    // Set default tab
    document.querySelector('.tab-button').click();
  }
}

// Load the tab when the page loads
window.onload = loadTab;

function adjustRows(textarea) {
  // Adjust the height regardless of content
  textarea.style.height = '96px'; // Reset height
  textarea.style.height = (textarea.scrollHeight) + 'px';
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
  textarea.addEventListener('paste', () => {
    // Use setTimeout to allow the paste operation to complete
    setTimeout(() => adjustRows(textarea), 0);
  });
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

function handleBindQuery() {
  document.querySelectorAll('.query-entry').forEach(item => {
    item.onclick = function() {
      document.getElementById('sql-input').value = this.textContent.trim();
      document.getElementById('nl-input').value = this.textContent.trim();
      // Adjust the height of both textareas after setting their values
      adjustRows(document.getElementById('sql-input'));
      adjustRows(document.getElementById('nl-input'));
    }
  });
}

// Initialize everything when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Add click event listeners to tab buttons
  document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', function(event) {
      openTab(event, this.getAttribute('data-tab'));
    });
  });

  // Initialize the right panel with the first database info if available
  updateDatabaseInfo();

  // Add event listeners for both dropdowns
  document.getElementById('selected_database_sql').addEventListener('change', updateDatabaseInfo);
  document.getElementById('selected_database_nl').addEventListener('change', updateDatabaseInfo);

  // Bind query entries
  handleBindQuery();

  // Load the initial tab
  loadTab();
});

document.addEventListener('DOMContentLoaded', function() {
  const themeDots = document.querySelectorAll('.theme-dot');
  const sqlInput = document.getElementById('sql-input');
  const nlInput = document.getElementById('nl-input');

  themeDots.forEach(dot => {
      dot.addEventListener('click', function() {
          // Remove active class from all dots
          themeDots.forEach(d => d.classList.remove('active'));
          // Add active class to clicked dot
          this.classList.add('active');

          // Apply theme to textarea
          const theme = this.getAttribute('data-theme');
          sqlInput.className = ''; // Reset classes
          sqlInput.classList.add(`theme-${theme}`);
          nlInput.className = ''; // Reset classes
          nlInput.classList.add(`theme-${theme}`);
      });
  });
});


