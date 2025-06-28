document.getElementById('voice-command-btn').addEventListener('click', function() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Speech recognition not supported. Use Google Chrome.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        fetch('/process_command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            const audio = document.getElementById('audio-feedback');
            audio.src = data.success ? '/static/audio/success.mp3' : '/static/audio/error.mp3';
            audio.play();
        });
    };

    recognition.start();
});
