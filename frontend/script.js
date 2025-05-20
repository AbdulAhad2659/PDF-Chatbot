document.addEventListener('DOMContentLoaded', () => {
    const pdfFile = document.getElementById('pdfFile');
    const uploadButton = document.getElementById('uploadButton');
    const uploadStatus = document.getElementById('uploadStatus');
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const chatHistoryDisplay = document.getElementById('chatHistoryDisplay');
    const uploadSection = document.querySelector('.upload-section');
    const chatInterface = document.querySelector('.chat-interface');
    const clearChatButton = document.getElementById('clearChatButton');
    const uploadAnotherButton = document.getElementById('uploadAnotherButton');

    function addMessageToChat(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', type === 'user' ? 'user-message' : 'bot-message');
        if (type === 'bot') {
            messageDiv.innerHTML = message;
            messageDiv.style.whiteSpace = 'pre-wrap';
        } else {
            messageDiv.textContent = message;
        }
        chatHistoryDisplay.appendChild(messageDiv);
        chatHistoryDisplay.scrollTop = chatHistoryDisplay.scrollHeight;
    }

    function clearChatDisplay() {
        chatHistoryDisplay.innerHTML = '';
    }

    uploadButton.addEventListener('click', async () => {
        const file = pdfFile.files[0];
        if (!file) {
            uploadStatus.textContent = 'Please select a PDF file.';
            uploadStatus.style.color = 'red';
            return;
        }

        uploadStatus.innerHTML = 'Uploading & Processing PDF... <div class="spinner"></div>';
        uploadStatus.style.color = 'black';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload_pdf/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                uploadStatus.textContent = data.message;
                uploadStatus.style.color = 'green';

                clearChatDisplay();
                addMessageToChat(`${data.message} You can now ask questions about <strong>${file.name}</strong>.`, 'bot');

                uploadSection.style.display = 'none';
                chatInterface.style.display = 'flex';
                pdfFile.value = '';
            } else {
                const errorData = await response.json();
                uploadStatus.textContent = `Upload failed: ${errorData.detail || response.statusText}`;
                uploadStatus.style.color = 'red';
            }
        } catch (error) {
            uploadStatus.textContent = 'Upload failed: Network error or server unavailable.';
            uploadStatus.style.color = 'red';
            console.error('Network error during PDF upload:', error);
        }
    });

    async function handleAskQuestion() {
        const question = questionInput.value.trim();
        if (!question) {
            alert('Please enter a question.');
            return;
        }

        addMessageToChat(question, 'user');
        questionInput.value = '';

        const thinkingMsgDiv = document.createElement('div');
        thinkingMsgDiv.classList.add('chat-message', 'bot-message');
        thinkingMsgDiv.innerHTML = '<div class="spinner" style="display:inline-block; vertical-align:middle; width:16px; height:16px;"></div>';
        chatHistoryDisplay.appendChild(thinkingMsgDiv);
        chatHistoryDisplay.scrollTop = chatHistoryDisplay.scrollHeight;

        const formData = new FormData();
        formData.append('question', question);

        try {
            const response = await fetch('/ask_question/', {
                method: 'POST',
                body: formData,
            });

            chatHistoryDisplay.removeChild(thinkingMsgDiv);

            if (response.ok) {
                const data = await response.json();
                addMessageToChat(data.answer, 'bot');
            } else {
                const errorData = await response.json();
                addMessageToChat(`Error: ${errorData.detail || response.statusText}`, 'bot');
            }
        } catch (error) {
            chatHistoryDisplay.removeChild(thinkingMsgDiv);
            addMessageToChat('Error: Network error or server unavailable.', 'bot');
            console.error('Network error during question answering:', error);
        }
    }

    askButton.addEventListener('click', handleAskQuestion);
    questionInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleAskQuestion();
        }
    });

    clearChatButton.addEventListener('click', async () => {
        addMessageToChat('Clearing chat...', 'bot');
        try {
            const response = await fetch('/clear_chat/', {
                method: 'POST',
            });
            if (response.ok) {
                const data = await response.json();
                clearChatDisplay();
                addMessageToChat(`${data.message}`, 'bot');
            } else {
                const errorData = await response.json();
                addMessageToChat(`Error clearing chat - ${errorData.detail || response.statusText}`, 'bot');
            }
        } catch (error) {
            addMessageToChat('Network error while attempting to clear chat.', 'bot');
            console.error('Network error during chat clearing:', error);
        }
    });

    uploadAnotherButton.addEventListener('click', () => {
        chatInterface.style.display = 'none';
        uploadSection.style.display = 'block';
        clearChatDisplay();
        uploadStatus.textContent = 'Ready to upload a new PDF.';
        uploadStatus.style.color = 'black';
        pdfFile.value = '';
    });
});