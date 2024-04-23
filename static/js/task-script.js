document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('upload-form').addEventListener('submit', async function(event) {
        //event.preventDefault(); // Prevent form submission

        const formData = new FormData(this);
        const loadingContainer = document.getElementById('loading-message');
        // Hide the task list
        const taskList = document.getElementById('task-list');
        if (taskList) {
            taskList.classList.add('hidden');
        }
        // Show the spinner
        loadingContainer.classList.remove('hidden'); 
        loadingContainer.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p id="loading-text">Thank you, let me look.</p>
        `;

        const messages = ["Hmm...New file.", "This is new for me.", "Wait, seems like a lot is going on here.", "I am still working on this.", "Tasks are on the way.", "Few more seconds."];
        let messageIndex = 0;
        
        const updateMessage = () => {
            if (messageIndex < messages.length) {
                document.getElementById('loading-text').textContent = messages[messageIndex++];
            }
        };

        setTimeout(updateMessage, 1000); // Update messages after 1 second and then every 10 seconds
        const messageInterval = setInterval(updateMessage, 10000);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Network response was not ok.');
            clearInterval(messageInterval); // Stop updating messages
            loadingContainer.innerHTML = `<p>Upload Complete! Your tasks are ready.</p>`;
        } catch (error) {
            console.error('Upload failed:', error);
            clearInterval(messageInterval); // Stop updating messages
            loadingContainer.innerHTML = `<p>Upload failed. Please try again.</p>`;
        }
    });
});
