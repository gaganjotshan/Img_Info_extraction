from dash import html, dcc

def create_initial_upload():
    return html.Div(
        dcc.Upload(
            html.Div([
                "Drag and Drop or ", 
                html.A('Select Files'),
                html.Br(),
                html.Small("Supports images and PDFs", style={'color': '#666', 'font-size': '12px'})
            ]),
            id='initial-upload', 
            className='upload-area', 
            multiple=False,
            accept='image/*,.pdf'  # Accept images and PDF files
        ),
        id='initial-upload-row'
    )

def create_image_display():
    return html.Div(
        html.Div([
            html.Img(id='displayed-image', className='displayed-image'),
            dcc.Upload(
                html.Div("Drop new image or PDF to replace", id='overlay-div', className='overlay-div'),
                id='overlay-upload', 
                multiple=False,
                accept='image/*,.pdf',  # Accept images and PDF files
                style={'position': 'absolute', 'top': '0', 'left': '0', 
                       'width': '100%', 'height': '100%', 'border': 'none'}
            )
        ], className='image-container'),
        id='image-display-row', style={'display': 'none'}
    )