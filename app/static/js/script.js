document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const terminalContent = document.getElementById('terminal-content');
    const terminalInputArea = document.getElementById('terminal-input-area');
    const inputForm = document.getElementById('input-form');
    const userInput = document.getElementById('user-input');
    const calculatorButtons = document.querySelector('.calculator-buttons');
    
    // Add event listeners to calculator buttons using event delegation
    calculatorButtons.addEventListener('click', function(e) {
        // Check if a button was clicked
        if (e.target.classList.contains('calc-button')) {
            const functionId = e.target.dataset.functionId;
            const functionName = e.target.dataset.functionName;
            
            // Activate the function
            activateFunction(functionId, functionName);
        }
    });
    
    // Auto-resize textarea as user types
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Handle form submission
    inputForm.addEventListener('submit', function(e) {
        // Always prevent default form submission
        e.preventDefault();
        
        // Get the hx-post attribute
        const postUrl = inputForm.getAttribute('hx-post');
        
        // If no URL is set, do nothing
        if (!postUrl) {
            return;
        }
        
        // Show loading indicator in terminal content
        const loadingDiv = document.createElement('div');
        loadingDiv.innerHTML = '<p>Processing...</p><div class="loading"></div>';
        terminalContent.innerHTML = '';
        terminalContent.appendChild(loadingDiv);
        
        // Get the user input
        const userInputValue = userInput.value.trim();
        
        // Make the AJAX request manually
        fetch(postUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `user_input=${encodeURIComponent(userInputValue)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            // Update the terminal content with the response
            terminalContent.innerHTML = data;
        })
        .catch(error => {
            // Show error in terminal
            terminalContent.innerHTML = `<p style="color: #e74c3c;">Error: ${error.message}</p>`;
        })
        .finally(() => {
            // Clear the input field
            userInput.value = '';
            userInput.style.height = 'auto';
        });
    });
});

// Function to activate a calculator function
function activateFunction(functionId, functionName) {
    // Get DOM elements
    const terminalContent = document.getElementById('terminal-content');
    const terminalInputArea = document.getElementById('terminal-input-area');
    const inputForm = document.getElementById('input-form');
    const userInput = document.getElementById('user-input');
    
    // Update the terminal content to show which function is active
    terminalContent.innerHTML = `<p>Selected function: <span style="color: #3498db; font-weight: bold;">${functionName}</span></p>`;
    
    // Show the input area
    terminalInputArea.style.display = 'block';
    
    // Set the form's post URL
    inputForm.setAttribute('hx-post', `/api/calculate/${functionId}`);
    
    // Focus on the input field
    setTimeout(() => {
        userInput.focus();
    }, 100);
} 