document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const audio = document.getElementById('paper-audio');
    const playBtn = document.getElementById('play-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const progressBar = document.getElementById('progress-bar');
    const transcript = document.getElementById('transcript');
    const currentTimeDisplay = document.getElementById('current-time');
    const durationDisplay = document.getElementById('duration');
    const questionButtons = document.querySelectorAll('.question-button');
    const transcriptSpans = document.querySelectorAll('.transcript-text span');
    
    // Initialize
    let currentActiveSpan = null;
    
    // Format time function (converts seconds to MM:SS format)
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }
    
    // Update progress bar and time displays
    function updateProgress() {
        const percentage = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = percentage + '%';
        currentTimeDisplay.textContent = formatTime(audio.currentTime);
        
        // Update active transcript span
        updateActiveTranscript();
    }
    
    // Update which transcript span is active based on current time
    function updateActiveTranscript() {
        const currentTime = audio.currentTime;
        
        // Remove active class from previous span
        if (currentActiveSpan) {
            currentActiveSpan.classList.remove('active');
        }
        
        // Find the span that corresponds to the current time
        for (const span of transcriptSpans) {
            const start = parseFloat(span.dataset.start);
            const end = parseFloat(span.dataset.end);
            
            if (currentTime >= start && currentTime < end) {
                span.classList.add('active');
                currentActiveSpan = span;
                
                // Scroll to the active span (with smooth scrolling)
                span.scrollIntoView({ behavior: 'smooth', block: 'center' });
                break;
            }
        }
    }
    
    // Event listeners
    
    // When audio metadata is loaded, update the duration display
    audio.addEventListener('loadedmetadata', function() {
        durationDisplay.textContent = formatTime(audio.duration);
    });
    
    // Update progress as audio plays
    audio.addEventListener('timeupdate', updateProgress);
    
    // Play button
    playBtn.addEventListener('click', function() {
        audio.play();
    });
    
    // Pause button
    pauseBtn.addEventListener('click', function() {
        audio.pause();
    });
    
    // Click on progress bar to seek
    document.querySelector('.audio-progress').addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const clickPosition = (e.clientX - rect.left) / rect.width;
        audio.currentTime = clickPosition * audio.duration;
    });
    
    // Question buttons to seek to specific timestamps
    questionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const timestamp = parseFloat(this.dataset.timestamp);
            audio.currentTime = timestamp;
            audio.play();
        });
    });
    
    // Transcript spans to seek to specific parts
    transcriptSpans.forEach(span => {
        span.addEventListener('click', function() {
            const start = parseFloat(this.dataset.start);
            audio.currentTime = start;
            audio.play();
        });
    });
    
    // Additional keyboard shortcuts for accessibility
    document.addEventListener('keydown', function(e) {
        // Space bar toggles play/pause
        if (e.code === 'Space' && document.activeElement.tagName !== 'BUTTON') {
            e.preventDefault();
            if (audio.paused) {
                audio.play();
            } else {
                audio.pause();
            }
        }
        
        // Left/right arrows seek backward/forward by 5 seconds
        if (e.code === 'ArrowLeft') {
            audio.currentTime = Math.max(0, audio.currentTime - 5);
        }
        
        if (e.code === 'ArrowRight') {
            audio.currentTime = Math.min(audio.duration, audio.currentTime + 5);
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
            // DOM elements
            const audio = document.getElementById('paper-audio');
            const topicButtons = document.querySelectorAll('.topic-button');
            const transcriptSpans = document.querySelectorAll('.transcript-text span');
            
            // Current active span in transcript
            let currentActiveSpan = null;
            
            // Update which transcript span is active based on current time
            function updateActiveTranscript() {
                const currentTime = audio.currentTime;
                
                // Remove active class from previous span
                if (currentActiveSpan) {
                    currentActiveSpan.classList.remove('active');
                }
                
                // Find the span that corresponds to the current time
                for (const span of transcriptSpans) {
                    const start = parseFloat(span.dataset.start);
                    const end = parseFloat(span.dataset.end);
                    
                    if (currentTime >= start && currentTime < end) {
                        span.classList.add('active');
                        currentActiveSpan = span;
                        
                        // Scroll to the active span
                        span.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        break;
                    }
                }
            }
            
            // Topic buttons to seek to specific timestamps
            topicButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const timestamp = parseFloat(this.dataset.timestamp);
                    try {
                        audio.currentTime = timestamp;
                        audio.play();
                    } catch (error) {
                        console.error('Error seeking to timestamp:', error);
                    }
                });
            });
            
            // Transcript spans to seek to specific parts
            transcriptSpans.forEach(span => {
                span.addEventListener('click', function() {
                    const start = parseFloat(this.dataset.start);
                    try {
                        audio.currentTime = start;
                        audio.play();
                    } catch (error) {
                        console.error('Error seeking from transcript click:', error);
                    }
                });
            });
            
            // Update transcript highlighting when audio plays
            audio.addEventListener('timeupdate', updateActiveTranscript);
            
            // Additional keyboard shortcuts for accessibility
            document.addEventListener('keydown', function(e) {
                // Space bar toggles play/pause when not focusing on a button
                if (e.code === 'Space' && document.activeElement.tagName !== 'BUTTON') {
                    e.preventDefault();
                    if (audio.paused) {
                        audio.play();
                    } else {
                        audio.pause();
                    }
                }
                
                // Left/right arrows seek backward/forward by 5 seconds
                if (e.code === 'ArrowLeft') {
                    audio.currentTime = Math.max(0, audio.currentTime - 5);
                }
                
                if (e.code === 'ArrowRight') {
                    audio.currentTime = Math.min(audio.duration, audio.currentTime + 5);
                }
            });
        });