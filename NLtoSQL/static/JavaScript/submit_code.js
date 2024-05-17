// $(document).ready(function() {
//   $('#codeForm').submit(function(event) {
//     event.preventDefault(); // Prevent the default form submission

//     const codeText = $('#code-input').val();

//     $.ajax({
//       type: 'POST',
//       url: '{% url "submit_code" %}', // Correctly resolving the URL
//       data: {
//         'code_text': codeText,
//         'csrfmiddlewaretoken': '{{ csrf_token }}'
//       },
//       success: function(response) {
//         $('#response-output').text(response.generated_code); 
//         $('#response-container').show();
//       },
//       error: function(error) {
//         console.error('Error:', error);
//       }
//     });
//   });
// });

// function copyToClipboard() {
//   const copyText = document.getElementById('response-output').innerText;
//   const textArea = document.createElement('textarea');
//   textArea.value = copyText;
//   document.body.appendChild(textArea);
//   textArea.select();
//   document.execCommand('copy');
//   document.body.removeChild(textArea);
//   alert('Copied to clipboard');
// }
