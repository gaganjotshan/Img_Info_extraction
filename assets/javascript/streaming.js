window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.streaming = {
    handleStreaming: function(n_clicks, container_style, image_data) {
        if (!n_clicks || container_style.display !== 'block' || !image_data) {
            return window.dash_clientside.no_update;
        }

        // Clean up any existing event source
        if (window.currentEventSource) {
            window.currentEventSource.close();
            window.currentEventSource = null;
        }

        console.log('Starting dual extraction process...');

        const eventSource = new EventSource('/stream_dual_extractions');
        let currentExtractionContent = '';
        let currentExtraction = 'yaml';

        eventSource.onmessage = function(event) {
            const data = event.data;
            
            if (data === "[EXTRACTION_SWITCH]") {
                // Save first extraction content and switch to second
                window.dash_clientside.set_props('final-extraction-content-yaml', {
                    children: currentExtractionContent
                });
                
                window.dash_clientside.set_props('collapsible-box-container-yaml', {
                    style: {display: 'block'}
                });
                
                // Reset for second extraction
                currentExtractionContent = '';
                currentExtraction = 'json';
                
                // Update status
                window.dash_clientside.set_props('current-extraction-status', {
                    children: 'Sélection des données ciblées...'
                });
                
                // Clear streaming display
                window.dash_clientside.set_props('llm-response', {
                    children: ''
                });
                
                return;
            }
            
            if (data === "[ALL_DONE]") {
                console.log("Both extractions finished.");
                eventSource.close();
                window.currentEventSource = null;
                
                // Save second extraction content
                window.dash_clientside.set_props('final-extraction-content-json', {
                    children: currentExtractionContent
                });
                
                window.dash_clientside.set_props('collapsible-box-container-json', {
                    style: {display: 'block'}
                });
                
                // Trigger update for human-readable display
                window.dash_clientside.set_props('json-data-store', {
                    data: Date.now() // Use timestamp to trigger callback
                });
                
                // Hide streaming container
                window.dash_clientside.set_props('extraction-result-container', {
                    style: {display: 'none'}
                });
                
                // Re-enable button
                window.dash_clientside.set_props('extract-data-button', {
                    disabled: false
                });
                
                return;
            }

            // Regular extraction content
            currentExtractionContent += data;
            window.dash_clientside.set_props('llm-response', {
                children: currentExtractionContent
            });
        };

        eventSource.onerror = function(error) {
            console.error("Streaming error:", error);
            eventSource.close();
            window.currentEventSource = null;
            
            // Re-enable button
            window.dash_clientside.set_props('extract-data-button', {
                disabled: false
            });
            
            // Hide loading container
            window.dash_clientside.set_props('response-loading-container', {
                style: {display: 'none'}
            });
        };

        window.currentEventSource = eventSource;
        
        return window.dash_clientside.no_update;
    }
};