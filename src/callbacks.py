from src.image_callbacks import (
    _register_handle_initial_upload,
    _register_handle_overlay_upload,
    _register_update_display
)

from src.extraction_callbacks import (
    _register_generate_extraction_callback,
    _register_collapse_callbacks,
    _register_streaming_clientside,
    _register_stream_route
)

from src.bl_summary_callbacks import (
    _register_update_human_readable,
    _register_save_changes_callback,
    _register_add_article_callback,
    _register_delete_article_callback,
    _register_show_save_button,
    _register_show_add_article_button
)

def register_callbacks(app):
    """Registers all callbacks for the Dash app"""
    _register_handle_initial_upload(app)
    _register_handle_overlay_upload(app)
    _register_update_display(app)
    _register_generate_extraction_callback(app)
    _register_collapse_callbacks(app)
    _register_streaming_clientside(app)
    _register_stream_route(app)
    _register_update_human_readable(app)
    _register_save_changes_callback(app)
    _register_add_article_callback(app)
    _register_delete_article_callback(app)
    _register_show_save_button(app)
    _register_show_add_article_button(app)
