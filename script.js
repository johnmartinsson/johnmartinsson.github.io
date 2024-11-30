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