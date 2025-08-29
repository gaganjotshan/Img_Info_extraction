from dash import html, dcc

from src.image_layout import (
    create_initial_upload, 
    create_image_display
)

from src.extraction_layout import (
    create_extraction_button, 
    create_collapsible_box, 
    create_streaming_container
)

from src.bl_summary_layout import create_human_readable_box

def create_layout():
    # Create header with logo and title
    header = html.Div(
        [
            html.Div(
                html.Img(src='assets/images/eiffage.png', className="logo"), 
                className="logo_container"
            ),
            html.Div(
                html.H1("Dématérialisation de bon de livraison", className="title"), 
                className="title_container"
            ),
        ],
        className="app-header"
    )
    
    return html.Div([
        header,
        html.Div([
            html.Div([
                create_initial_upload(),
                create_image_display(),
                dcc.Store(id='stored-image', data=None),
                dcc.Store(id='json-data-store', data=None)
            ], className="flex-child left-column"),
            html.Div([
                create_extraction_button(),
                create_collapsible_box('yaml', 'Données extraites (YAML)'),
                create_collapsible_box('json', 'Données ciblées (JSON)'),
                create_human_readable_box(),
                create_streaming_container(),
            ], className="flex-child right-column")
        ], className='flex-container')
    ])