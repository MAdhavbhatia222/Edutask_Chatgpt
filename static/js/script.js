let message = "Hi, I will help you get next 1 week's tasks out of your syllabus.";
let index = 0;
let typingMessage = document.getElementById('typing-message');
let skipBtn = document.getElementById('skip-btn');
let initialMessage = document.getElementById('initial-message');
let uploadContainer = document.getElementById('upload-container');
let loadingMessagesDiv = document.getElementById('loading-messages');

function typeMessage() {
    if (index < message.length) {
        typingMessage.innerHTML += message.charAt(index);
        index++;
        const typingSpeed = 100 + Math.random() * 100; // Mimic natural typing rhythm
        setTimeout(typeMessage, typingSpeed);
    }
}


skipBtn.addEventListener('click', function() {
    initialMessage.classList.add('hidden');
    uploadContainer.classList.remove('hidden');
});

document.addEventListener('DOMContentLoaded', (event) => {
    typeMessage();
});

setTimeout(() => {
    if (index < message.length) {
        typingMessage.innerHTML = message;
    }
    initialMessage.classList.add('hidden');
    uploadContainer.classList.remove('hidden');
}, 10000);

document.getElementById('upload-form').addEventListener('submit', function(event) {
    //event.preventDefault(); // Prevent the actual form submission

    // Step 1: Display the success message
    loadingMessagesDiv.innerHTML = "File uploaded successfully!";

    // Step 2: After a short delay, show the spinning wheel
    setTimeout(() => {
        const spinnerHtml =  `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p id="loading-text">Thank you, let me look.</p>
    `;
        loadingMessagesDiv.innerHTML = spinnerHtml;
		const messages = ["Hmm...New file.", "This is new for me.", "This might take a while.", "I am still working on this.", "Tasks are on the way.", "Few more seconds."];
		let messageIndex = 0;

		const updateMessage = () => {
			if (messageIndex < messages.length) {
				document.getElementById('loading-text').textContent = messages[messageIndex++];
			}
		};

		setTimeout(updateMessage, 1000); // Update messages after 1 second and then every 10 seconds
		const messageInterval = setInterval(updateMessage, 10000);
		
        // Step 3: After some time, you can redirect or show the next content
        setTimeout(() => {
            console.log("Next page or action goes here.");
        }, 5000); // Adjust the delay as needed before taking the next action

    }, 2000); // Adjust this delay based on how long you want the success message to show
});


