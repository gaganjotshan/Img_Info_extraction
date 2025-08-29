from dash import Input, Output, State, ClientsideFunction
from flask import Response

from src.prompt_config import YAML_EXTRACTION_PROMPT, JSON_EXTRACTION_PROMPT
from src.utils import stream_response

# ========== Data Extraction Callbacks ==========
def _register_generate_extraction_callback(app):
    """Handles data extraction button click"""
    @app.callback(
        [Output('extraction-result-container', 'style'),
        Output('response-loading-container', 'style'),
        Output('llm-response', 'children'),
        Output('extract-data-button', 'disabled'),
        Output('collapsible-box-container-yaml', 'style'),
        Output('collapsible-box-container-json', 'style'),
        Output('current-extraction-status', 'children'),
        Output('json-data-store', 'data')],  # Add JSON data store output
        [Input('extract-data-button', 'n_clicks')],
        [State('stored-image', 'data')],
        prevent_initial_call=True
    )
    def handle_generate_extraction(n_clicks, image_data):
        # Reset JSON data when starting new extraction
        app.extracted_json_data = None
        
        # Check if image is uploaded
        if not image_data:
            return (
                {'display': 'none'},   # Hide extraction result container
                {'display': 'none'},   # Hide loading container
                "Veuillez d'abord télécharger une image.",  # Show error message
                False,                 # Keep button enabled
                {'display': 'none'},   # Hide yaml box
                {'display': 'none'},   # Hide json box
                '',                    # Clear status
                None                   # Clear JSON data store
            )
            
        return (
            {'display': 'block'},  # Show extraction result container
            {'display': 'flex'},   # Show loading container
            "",                    # Clear previous response
            True,                  # Disable button during streaming
            {'display': 'none'},   # Hide yaml box during generation
            {'display': 'none'},   # Hide json box during generation
            'Extraction des données en cours...',  # Initial status
            None                   # Clear JSON data store
        )

# ========== Collapsible Section Callbacks ==========

def _register_collapse_callbacks(app):
    """Registers collapsible section interactions"""
    # YAML extraction collapsible
    @app.callback(
        [Output('collapsible-content-yaml', 'className'),
        Output('collapse-arrow-yaml', 'children'),
        Output('collapse-arrow-yaml', 'className')],
        [Input('collapse-button-yaml', 'n_clicks')],
        [State('collapsible-content-yaml', 'className')],
        prevent_initial_call=True
    )
    def toggle_collapse_yaml(n_clicks, current_class):
        is_collapsed = 'collapsed' in current_class if current_class else False
        
        if is_collapsed:
            # Expand
            return (
                'collapsible-content expanded',
                '⮟',
                'collapse-arrow'
            )
        else:
            # Collapse
            return (
                'collapsible-content collapsed',
                '⮞',
                'collapse-arrow rotated'
            )

    # JSON extraction collapsible
    @app.callback(
        [Output('collapsible-content-json', 'className'),
        Output('collapse-arrow-json', 'children'),
        Output('collapse-arrow-json', 'className')],
        [Input('collapse-button-json', 'n_clicks')],
        [State('collapsible-content-json', 'className')],
        prevent_initial_call=True
    )
    def toggle_collapse_json(n_clicks, current_class):
        is_collapsed = 'collapsed' in current_class if current_class else False
        
        if is_collapsed:
            # Expand
            return (
                'collapsible-content expanded',
                '⮟',
                'collapse-arrow'
            )
        else:
            # Collapse
            return (
                'collapsible-content collapsed',
                '⮞',
                'collapse-arrow rotated'
            )

# ========== Streaming Callbacks ==========

def _register_streaming_clientside(app):
    app.clientside_callback(
        ClientsideFunction(
            namespace='streaming',
            function_name='handleStreaming'
        ),
        Output('llm-response', 'id'),
        [Input('extract-data-button', 'n_clicks'),
         Input('extraction-result-container', 'style'),
         Input('stored-image', 'data')]
    )

def _register_stream_route(app):
    """Server-side route for dual extraction streaming"""
    @app.server.route("/stream_dual_extractions")
    def stream_dual_extractions():
        def generate():
            try:
                
                # Check if image is available
                if not app.current_image_data:
                    yield f"data: Erreur: Aucune image disponible.\n\n"
                    yield f"data: [ALL_DONE]\n\n"
                    return

                # Extract base64 image data from data URL
                if app.current_image_data.startswith('data:'):
                    encoded_image = app.current_image_data.split(',')[1]
                else:
                    encoded_image = app.current_image_data
                
                collected_response = []
                # Generate first extraction (YAML)
                for token in stream_response(model="qwen2.5vl:72b", prompt=YAML_EXTRACTION_PROMPT, images=encoded_image):
                    collected_response.append(token)
                    lines = token.split('\n')
                    for line in lines:
                        yield f"data: {line}\n"
                    yield "\n"
                
                response = ''.join(collected_response)

                # Signal extraction switch
                yield f"data: [EXTRACTION_SWITCH]\n\n"
                
                # Generate second extraction (JSON) and collect it
                json_response_parts = []
                for token in stream_response(model="qwen2.5vl:72b", prompt=JSON_EXTRACTION_PROMPT+response):
                    json_response_parts.append(token)
                    lines = token.split('\n')
                    for line in lines:
                        yield f"data: {line}\n"
                    yield "\n"
                
                # Store the complete JSON response in global variable
                complete_json_response = ''.join(json_response_parts)
                
                # Try to extract just the JSON part from the response
                try:
                    # Look for JSON content between ```json and ``` or just valid JSON
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', complete_json_response, re.DOTALL)
                    if json_match:
                        app.extracted_json_data = json_match.group(1)
                    else:
                        # Try to find standalone JSON object
                        json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', complete_json_response, re.DOTALL)
                        if json_match:
                            app.extracted_json_data = json_match.group(1)
                        else:
                            app.extracted_json_data = complete_json_response
                except Exception as e:
                    print(f"JSON extraction error: {e}")
                    app.extracted_json_data = complete_json_response
                    
            except Exception as e:
                print(f"Streaming error: {e}")
                yield f"data: Erreur: {str(e)}\n\n"
            finally:
                yield f"data: [ALL_DONE]\n\n"

        return Response(generate(), mimetype='text/event-stream')
