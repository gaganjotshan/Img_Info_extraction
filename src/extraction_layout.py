from dash import html, dcc

def create_extraction_button():
    return html.Div(
        html.Button(
            [html.Span('⋗'), html.Span('Extraire les données', className='button-text')],
            id='extract-data-button',
            className='extraction-button'
        ),
        className='extraction-button-container',
    )

def create_collapsible_box(extraction_id, title):
    return html.Div(
        html.Div([
            html.Button(
                html.Div([
                    html.Span(title, className='title-text'),
                    html.Span('⮞', id=f'collapse-arrow-{extraction_id}', className='collapse-arrow rotated')
                ], className='button-inner'),
                id=f'collapse-button-{extraction_id}', className='collapse-button'
            ),
            html.Div(
                html.Div(dcc.Markdown(id=f'final-extraction-content-{extraction_id}'), className='markdown-container'),
                id=f'collapsible-content-{extraction_id}', className='collapsible-content collapsed'
            )
        ], className='collapsible-box'),
        id=f'collapsible-box-container-{extraction_id}', className='collapsible-container',
        style={'display': 'none'}
    )

def create_streaming_container():
    return html.Div([
        html.Div(
            html.Div("Extraction YAML en cours...", id='current-extraction-status'),
            id="response-loading-container", style={'display': 'none'}
        ),
        html.Div(dcc.Markdown(id='llm-response'), className='markdown-container')
    ], id='extraction-result-container', className='extraction-result-container', style={'display': 'none'})