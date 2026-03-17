const API_BASE = '/api';
let availableReferenceVoices = {};

// Timer variables
let startTime = null;
let timerInterval = null;

// Helper function to format time in mm:ss format
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}m:${remainingSeconds.toString().padStart(2, '0')}s`;
}

// Initialize the page
document.addEventListener( 'DOMContentLoaded', function () {
    // checkHealth();
    // loadReferenceVoices();
    // loadGeneratedFiles();
    addBatchItem(); // Add initial batch item

    // Setup single TTS form
    document.getElementById( 'singleTTSForm' ).addEventListener( 'submit', function ( e ) {
    e.preventDefault();
    generateSingleTTS();
    } );

    // Setup file selection handler for reference voice
    document.getElementById( 'referenceVoiceFile' ).addEventListener( 'change', function ( e ) {
    const file = e.target.files[0];
    if ( file ) {
        const uniqueName = generateUniqueReferenceVoiceName( file.name );
        document.getElementById( 'referenceVoiceName' ).value = uniqueName;
    }
    } );
} );


// Timer functions
function startTimer() {
    startTime = Date.now();
    const elapsedTimeElement = document.getElementById('elapsedTime');
    
    timerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    elapsedTimeElement.textContent = formatTime(elapsed);
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
    }
}

// Batch timer functions
let batchStartTime = null;
let batchTimerInterval = null;

function startBatchTimer() {
    batchStartTime = Date.now();
    const elapsedTimeElement = document.getElementById('batchElapsedTime');
    
    batchTimerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - batchStartTime) / 1000);
    elapsedTimeElement.textContent = formatTime(elapsed);
    }, 1000);
}

function stopBatchTimer() {
    if (batchTimerInterval) {
    clearInterval(batchTimerInterval);
    batchTimerInterval = null;
    }
}


async function generateSingleTTS() {
    const text = document.getElementById( 'singleText' ).value;
    const referenceVoiceKey = document.getElementById( 'singleReferenceVoice' ).value;
    const format = document.getElementById( 'singleFormat' ).value;
    const sampleRate = parseInt( document.getElementById( 'sampleRate' ).value );
    const normalize = document.getElementById( 'normalize' ).checked;
    const seed = parseInt( document.getElementById( 'seed' ).value );

    const resultDiv = document.getElementById( 'singleResult' );
    const loadingDiv = document.getElementById( 'singleLoading' );
    const submitBtn = document.querySelector( '#singleTTSForm button[type="submit"]' );

    resultDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    submitBtn.disabled = true;

    // Start timer and system monitoring
    startTimer();
    startSystemMonitoring();

    try {
    const response = await fetch( `${API_BASE}/tts`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify( {
        text: text,
        reference_voice_key: referenceVoiceKey,
        output_format: format,
        sample_rate: sampleRate,
        normalize: normalize,
        seed: seed
        } )
    } );

    const data = await response.json();

    // Stop timer and system monitoring
    stopTimer();
    stopSystemMonitoring();

    loadingDiv.style.display = 'none';
    submitBtn.disabled = false;

    if ( response.ok && data.success ) {
        resultDiv.className = 'block mt-4 p-4 rounded-lg bg-green-800 border border-green-600';
        resultDiv.innerHTML = `
        <div class="text-green-200">
            <div class="flex items-center mb-2">
            <span class="mr-2">✅</span>
            <span class="font-semibold">Speech generated successfully!</span>
            </div>
            <div class="text-sm space-y-1">
            <div>Duration: ${formatTime(Math.floor(data.duration))}</div>
            <div>Filename: ${data.filename}</div>
            <div>Used Seed: ${data.used_seed || 'N/A'}</div>
            <div>File saved to server output directory</div>
            </div>
            <audio controls class="w-full mt-3 h-8" style="filter: hue-rotate(90deg);">
            <source src="data:audio/${format};base64,${data.audio_base64}" type="audio/${format}">
            Your browser does not support the audio element.
            </audio>
            <div class="mt-3 flex gap-2">
            <button onclick="downloadFileFromServer('${data.filename}')" 
                class="bg-chalk-600 hover:bg-chalk-500 text-chalkboard-900 px-3 py-1 rounded-md text-sm">
                📥 Download
            </button>
            <button onclick="document.getElementById('seed').value = '${data.used_seed || -1}'" 
                class="bg-chalk-600 hover:bg-chalk-500 text-chalkboard-900 px-3 py-1 rounded-md text-sm">
                🎯 Use This Seed
            </button>
            </div>
        </div>
        `;
        resultDiv.style.display = 'block';
        loadGeneratedFiles();
    } else {
        resultDiv.className = 'block mt-4 p-4 rounded-lg bg-red-800 border border-red-600';
        resultDiv.innerHTML = `
        <div class="text-red-200">
            <span class="mr-2">❌</span>
            <span>Error: ${data.detail || data.message || 'Unknown error'}</span>
        </div>
        `;
        resultDiv.style.display = 'block';
    }

    } catch ( error ) {
    // Stop timer and system monitoring on error
    stopTimer();
    stopSystemMonitoring();

    loadingDiv.style.display = 'none';
    submitBtn.disabled = false;
    resultDiv.className = 'block mt-4 p-4 rounded-lg bg-red-800 border border-red-600';
    resultDiv.innerHTML = `
        <div class="text-red-200">
        <span class="mr-2">❌</span>
        <span>Network error: ${error.message}</span>
        </div>
    `;
    resultDiv.style.display = 'block';
    }
}

function addBatchItem() {
    const container = document.getElementById( 'batchContainer' );
    const itemCount = container.children.length;

    const newItem = document.createElement( 'div' );
    newItem.className = 'batch-item bg-chalkboard-800 border border-chalk-700 rounded-lg p-3';
    newItem.innerHTML = `
    <div class="flex items-center justify-between mb-2">
        <span class="text-chalk-200 font-semibold">Item ${itemCount + 1}</span>
        <button type="button" onclick="removeBatchItem(this)" class="text-red-400 hover:text-red-300 text-sm">
        ❌ Remove
        </button>
    </div>
    <div class="space-y-2">
        <textarea class="batch-text w-full h-20 bg-chalkboard-700 border border-chalk-600 text-chalk-100 rounded-md p-2 text-sm placeholder-chalk-400 focus:border-chalk-500 focus:outline-none resize-none" placeholder="Enter text..."></textarea>
        <select class="batch-reference-voice w-full bg-chalkboard-700 border border-chalk-600 text-chalk-100 rounded-md p-2 text-sm focus:border-chalk-500 focus:outline-none">
        <option value="">Select a reference voice...</option>
        </select>
    </div>
    `;
    container.appendChild( newItem );
    updateReferenceVoicesSelects();
}

function removeBatchItem( button ) {
    const items = document.querySelectorAll( '.batch-item' );
    if ( items.length > 1 ) {
    button.closest( '.batch-item' ).remove();
    }
}

async function processBatch() {
    const batchItems = document.querySelectorAll( '.batch-item' );
    const requests = [];

    for ( const item of batchItems ) {
    const text = item.querySelector( '.batch-text' ).value;
    const referenceVoiceKey = item.querySelector( '.batch-reference-voice' ).value;

    if ( text && referenceVoiceKey ) {
        requests.push( {
        text: text,
        reference_voice_key: referenceVoiceKey,
        output_format: 'wav',
        sample_rate: 24000,
        normalize: true
        } );
    }
    }

    if ( requests.length === 0 ) {
    alert( 'Please add at least one valid request' );
    return;
    }

    const resultDiv = document.getElementById( 'batchResult' );
    const loadingDiv = document.getElementById( 'batchLoading' );

    resultDiv.style.display = 'none';
    loadingDiv.style.display = 'block';

    // Start batch timer and system monitoring for batch processing
    startBatchTimer();
    startSystemMonitoring( 'batch' );

    try {
    const response = await fetch( `${API_BASE}/tts/batch`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify( {
        requests: requests,
        return_as_zip: false
        } )
    } );

    const data = await response.json();

    // Stop batch timer and system monitoring
    stopBatchTimer();
    stopSystemMonitoring();

    loadingDiv.style.display = 'none';

    if ( response.ok ) {
        let resultHtml = `
        <div class="bg-chalkboard-800 border border-chalk-600 rounded-lg p-4">
            <h4 class="font-semibold text-chalk-100 mb-3">📊 Batch Results</h4>
            <div class="grid grid-cols-2 gap-4 text-sm text-chalk-300 mb-4">
            <div>Total: ${data.total_requests}</div>
            <div>Successful: ${data.successful_requests}</div>
            <div>Failed: ${data.failed_requests}</div>
            <div>Duration: ${formatTime(Math.floor(data.total_duration))}</div>
            </div>
            <div class="space-y-3">
        `;

        data.results.forEach( ( result, index ) => {
        if ( result.success ) {
            resultHtml += `
            <div class="bg-green-800 border border-green-600 rounded-md p-3">
                <div class="text-green-200">
                <strong>Item ${index + 1}:</strong> ✅ Success
                <div class="text-xs mt-1">File: ${result.filename}</div>
                <audio controls class="w-full mt-2 h-8" style="filter: hue-rotate(90deg);">
                    <source src="data:audio/wav;base64,${result.audio_base64}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <button onclick="downloadFileFromServer('${result.filename}')" 
                    class="mt-2 bg-chalk-600 hover:bg-chalk-500 text-chalkboard-900 px-2 py-1 rounded text-xs">
                    📥 Download
                </button>
                </div>
            </div>
            `;
        } else {
            resultHtml += `
            <div class="bg-red-800 border border-red-600 rounded-md p-3">
                <div class="text-red-200">
                <strong>Item ${index + 1}:</strong> ❌ Failed<br>
                <small>${result.message}</small>
                </div>
            </div>
            `;
        }
        } );

        resultHtml += '</div></div>';

        loadGeneratedFiles();

        resultDiv.className = 'block mt-4';
        resultDiv.innerHTML = resultHtml;
        resultDiv.style.display = 'block';
    } else {
        resultDiv.className = 'block mt-4 p-4 rounded-lg bg-red-800 border border-red-600';
        resultDiv.innerHTML = `
        <div class="text-red-200">
            <span class="mr-2">❌</span>
            <span>Batch processing failed: ${data.detail || 'Unknown error'}</span>
        </div>
        `;
        resultDiv.style.display = 'block';
    }

    } catch ( error ) {
    // Stop batch timer and system monitoring on error
    stopBatchTimer();
    stopSystemMonitoring();

    loadingDiv.style.display = 'none';
    resultDiv.className = 'block mt-4 p-4 rounded-lg bg-red-800 border border-red-600';
    resultDiv.innerHTML = `
        <div class="text-red-200">
        <span class="mr-2">❌</span>
        <span>Network error: ${error.message}</span>
        </div>
    `;
    resultDiv.style.display = 'block';
    }
}
