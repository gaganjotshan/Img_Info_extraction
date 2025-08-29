import dash
from dash import html, Input, Output, State, ALL, ctx
import json

from src.bl_summary_layout import create_human_readable_content

# Helper function to save current state
def _save_current_state(app, field_ids, field_values, article_ids, article_values):
    """Save current form state to app.extracted_json_data"""
    try:
        if app.extracted_json_data:
            data = json.loads(app.extracted_json_data)
        else:
            return False
        
        # Update top-level fields
        for field_id, value in zip(field_ids, field_values):
            field_path = field_id['field'].split('.')
            if len(field_path) == 1:
                data[field_path[0]] = value
            elif len(field_path) == 2:
                if field_path[0] not in data:
                    data[field_path[0]] = {}
                data[field_path[0]][field_path[1]] = value
        
        # Update articles
        article_map = {}
        for article_id, value in zip(article_ids, article_values):
            index = article_id['index'] - 1  # Convert to 0-based index
            field = article_id['field']
            
            if index not in article_map:
                article_map[index] = {}
            
            # Handle numeric fields
            if field in ['quantity', 'unit_price'] and value:
                try:
                    article_map[index][field] = float(value)
                except ValueError:
                    article_map[index][field] = value
            else:
                article_map[index][field] = value
        
        # Apply article updates
        if 'articles' in data and isinstance(data['articles'], list):
            for index, updates in article_map.items():
                if index < len(data['articles']):
                    data['articles'][index].update(updates)
        
        # Update global variable with new data
        app.extracted_json_data = json.dumps(data, indent=2)
        return True
        
    except Exception as e:
        print(f"Error auto-saving: {e}")
        return False

# Update human-readable display when JSON data is available
def _register_update_human_readable(app):
    @app.callback(
        Output('human-readable-container', 'style'),
        Output('human-readable-content', 'children'),
        Input('json-data-store', 'data')
    )
    def update_human_readable_display(json_data):
        if app.extracted_json_data:
            try:
                data = json.loads(app.extracted_json_data)
                return {'display': 'block'}, create_human_readable_content(data)
            except (json.JSONDecodeError, TypeError):
                return {'display': 'none'}, ""
        return {'display': 'none'}, ""

# Add callback for saving changes
def _register_save_changes_callback(app):
    @app.callback(
        [Output('json-data-store', 'data', allow_duplicate=True),
         Output('save-status-message', 'children')],
        Input('save-changes-button', 'n_clicks'),
        [State('json-data-store', 'data'),
         State({'type': 'editable-field', 'field': ALL}, 'id'),
         State({'type': 'editable-field', 'field': ALL}, 'value'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'id'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'value')],
        prevent_initial_call=True
    )
    def save_changes(n_clicks, current_data, field_ids, field_values, article_ids, article_values):
        if n_clicks is None:
            return dash.no_update, ""
        
        success = _save_current_state(app, field_ids, field_values, article_ids, article_values)
        
        if success:
            return app.extracted_json_data, html.Span("Modifications enregistrées avec succès !", className="save-success")
        else:
            return dash.no_update, html.Span("Erreur lors de la sauvegarde", className="save-error")

# Add callback for adding new articles (with auto-save)
def _register_add_article_callback(app):
    @app.callback(
        [Output('json-data-store', 'data', allow_duplicate=True),
         Output('human-readable-content', 'children', allow_duplicate=True),
         Output('save-status-message', 'children', allow_duplicate=True)],
        Input('add-article-button', 'n_clicks'),
        [State('json-data-store', 'data'),
         State({'type': 'editable-field', 'field': ALL}, 'id'),
         State({'type': 'editable-field', 'field': ALL}, 'value'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'id'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'value')],
        prevent_initial_call=True
    )
    def add_article(n_clicks, current_data, field_ids, field_values, article_ids, article_values):
        if n_clicks is None or n_clicks == 0:
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # First, auto-save current state
            auto_save_success = _save_current_state(app, field_ids, field_values, article_ids, article_values)
            
            # Parse current JSON data
            if app.extracted_json_data:
                data = json.loads(app.extracted_json_data)
            else:
                return dash.no_update, dash.no_update, html.Span("Aucune donnée disponible", className="save-error")
            
            # Ensure articles list exists
            if 'articles' not in data:
                data['articles'] = []
            
            # Add new empty article
            new_article = {
                'code': '',
                'description': '',
                'quantity': 0,
                'unit': '',
                'unit_price': 0.0
            }
            
            data['articles'].append(new_article)
            
            # Update global variable with new data
            app.extracted_json_data = json.dumps(data, indent=2)
            
            # Return updated data and refresh the content
            return app.extracted_json_data, create_human_readable_content(data), ""
        
        except Exception as e:
            print(f"Error adding article: {e}")
            return dash.no_update, dash.no_update, html.Span(f"Erreur: {str(e)}", className="save-error")

# Add callback for deleting articles (with auto-save)
def _register_delete_article_callback(app):
    @app.callback(
        [Output('json-data-store', 'data', allow_duplicate=True),
         Output('human-readable-content', 'children', allow_duplicate=True),
         Output('save-status-message', 'children', allow_duplicate=True)],
        Input({'type': 'delete-article-button', 'index': ALL}, 'n_clicks'),
        [State('json-data-store', 'data'),
         State({'type': 'editable-field', 'field': ALL}, 'id'),
         State({'type': 'editable-field', 'field': ALL}, 'value'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'id'),
         State({'type': 'editable-article', 'index': ALL, 'field': ALL}, 'value')],
        prevent_initial_call=True
    )
    def delete_article(n_clicks_list, current_data, field_ids, field_values, article_ids, article_values):
        # Check if any delete button was clicked
        if not n_clicks_list or all(clicks is None or clicks == 0 for clicks in n_clicks_list):
            return dash.no_update, dash.no_update, dash.no_update
        
        # Find which button was clicked
        clicked_index = None
        for i, clicks in enumerate(n_clicks_list):
            if clicks and clicks > 0:
                # Get the actual index from the triggered callback context
                if ctx.triggered:
                    trigger_id = ctx.triggered[0]['prop_id']
                    if 'delete-article-button' in trigger_id:
                        # Extract index from the trigger ID
                        import re
                        match = re.search(r'"index":(\d+)', trigger_id)
                        if match:
                            clicked_index = int(match.group(1)) - 1  # Convert to 0-based index
                            break
        
        if clicked_index is None:
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # First, auto-save current state
            auto_save_success = _save_current_state(app, field_ids, field_values, article_ids, article_values)
            
            # Parse current JSON data
            if app.extracted_json_data:
                data = json.loads(app.extracted_json_data)
            else:
                return dash.no_update, dash.no_update, html.Span("Aucune donnée disponible", className="save-error")
            
            # Ensure articles list exists
            if 'articles' not in data or not isinstance(data['articles'], list):
                return dash.no_update, dash.no_update, html.Span("Aucun article à supprimer", className="save-error")
            
            # Check if index is valid
            if clicked_index < 0 or clicked_index >= len(data['articles']):
                return dash.no_update, dash.no_update, html.Span("Index d'article invalide", className="save-error")
            
            # Remove the article at the specified index
            deleted_article = data['articles'].pop(clicked_index)
            
            # Update global variable with new data
            app.extracted_json_data = json.dumps(data, indent=2)
            
            # Return updated data and refresh the content
            return app.extracted_json_data, create_human_readable_content(data), ""
        
        except Exception as e:
            print(f"Error deleting article: {e}")
            return dash.no_update, dash.no_update, html.Span(f"Erreur: {str(e)}", className="save-error")

# Add a callback to show/hide the save button when content is available
def _register_show_save_button(app):
    @app.callback(
        Output('save-changes-button', 'style'),
        Input('human-readable-content', 'children')
    )
    def show_save_button(content):
        if content:
            return {'display': 'block'}
        return {'display': 'none'}

# Add a callback to show/hide the add-article button when content is available
def _register_show_add_article_button(app):
    @app.callback(
        Output('add-article-button', 'style'),
        Input('human-readable-content', 'children')
    )
    def show_add_article_button(content):
        if content:
            return {'display': 'block'}
        return {'display': 'none'}

# Register all callbacks
def register_callbacks(app):
    _register_update_human_readable(app)
    _register_save_changes_callback(app)
    _register_add_article_callback(app)
    _register_delete_article_callback(app)
    _register_show_save_button(app)
    _register_show_add_article_button(app)