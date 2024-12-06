// script.js
function playSound(id) {
    var audio = document.getElementById(id);
    if (audio.paused) {
        audio.play();
    } else {
        audio.pause();
        audio.currentTime = 0;
    }
}

function togglePlayPause(id, element) {
    var audio = document.getElementById(id);
    var icon = element.querySelector('.play-pause-icon');
    if (audio.paused) {
        audio.play();
        icon.classList.remove('play');
        icon.classList.add('pause');
    } else {
        audio.pause();
        audio.currentTime = 0;
        icon.classList.remove('pause');
        icon.classList.add('play');
    }

    // Add event listener for the 'ended' event
    audio.addEventListener('ended', function() {
        icon.classList.remove('pause');
        icon.classList.add('play');
    });
}

// Function to load audio when needed
function loadAudioOnPlay(audioId, sourceId, src) {
    var audio = document.getElementById(audioId);
    var audioSource = document.getElementById(sourceId);
    audio.addEventListener('play', function() {
        if (!audioSource.src) {
            audioSource.src = src;
            audio.load();
        }
    });
}

// Call the function to load audio when needed
loadAudioOnPlay('audio-about-me', 'audio-source-about-me', '/audio/about-me.webm');