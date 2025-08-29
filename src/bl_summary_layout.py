from dash import html, dcc

def create_human_readable_box():
    return html.Div(
        html.Div([
            html.H3("Résumé du bon de Livraison", className="human-readable-title"),
            html.Div(id='human-readable-content'),
            # Add the add-article button in the initial layout (hidden initially)
            html.Div([
                html.Button(
                    "➕ Ajouter un article",
                    id="add-article-button",
                    className="add-article-button",
                    n_clicks=0,
                    style={'display': 'none'}  # Hide initially
                )
            ], className="section exception1"),
            # Add the save button and status message here in the initial layout
            html.Div([
                html.Div([
                    html.Button(
                        "Enregistrer les modifications",
                        id="save-changes-button",
                        className="save-button",
                        style={'display': 'none'}  # Hide initially
                    )
                ], className="save-button-container"),
                html.Div(id="save-status-message", className="save-status")
            ], className="save-section")
        ], className='human-readable-box'),
        id='human-readable-container', className='human-readable-container',
        style={'display': 'none'}
    )

def create_human_readable_content(data):
    """Create an editable human-readable display of the JSON data"""
    if not data:
        return html.Div("Aucune donnée disponible")
    
    content = []
    
    # Header section - editable
    content.append(html.Div([
        html.H4("Bon de Livraison", className="section-title"),
        html.Div([
            html.Span("N° BL: ", className="label"),
            dcc.Input(
                id={'type': 'editable-field', 'field': 'bl_number'},
                value=data.get('bl_number', ''),
                className='editable-input',
                placeholder='Numéro de bon de livraison'
            )
        ], className="info-row"),
        html.Div([
            html.Span("N° Commande: ", className="label"), 
            dcc.Input(
                id={'type': 'editable-field', 'field': 'order_number'},
                value=data.get('order_number', ''),
                className='editable-input',
                placeholder='Numéro de commande'
            )
        ], className="info-row")
    ], className="section"))
    
    # Supplier section - editable
    supplier = data.get('supplier', {})
    content.append(html.Div([
        html.H4("Fournisseur", className="section-title"),
        html.Div([
            html.Span("Nom: ", className="label"),
            dcc.Input(
                id={'type': 'editable-field', 'field': 'supplier.name'},
                value=supplier.get('name', ''),
                className='editable-input',
                placeholder='Nom du fournisseur'
            )
        ], className="info-row"),
        html.Div([
            html.Span("SIREN: ", className="label"),
            dcc.Input(
                id={'type': 'editable-field', 'field': 'supplier.siren'},
                value=supplier.get('siren', ''),
                className='editable-input',
                placeholder='Numéro SIREN (9 chiffres)'
            )
        ], className="info-row"),
        html.Div([
            html.Span("SIRET: ", className="label"),
            dcc.Input(
                id={'type': 'editable-field', 'field': 'supplier.siret'},
                value=supplier.get('siret', ''),
                className='editable-input',
                placeholder='Numéro SIRET (14 chiffres)'
            )
        ], className="info-row"),
        html.Div([
            html.Span("Adresse: ", className="label"),
            dcc.Textarea(
                id={'type': 'editable-field', 'field': 'supplier.address'},
                value=supplier.get('address', ''),
                className='editable-textarea',
                placeholder='Adresse complète du fournisseur'
            )
        ], className="info-row")
    ], className="section"))
    
    # Articles section - editable with add/delete functionality
    articles = data.get('articles', [])
    
    # Articles header (no add button here since it's in the main layout now)
    articles_header = html.Div([
        html.H4("Articles", className="section-title")
    ], className="articles-header")
    
    if articles:
        article_rows = []
        total_value = 0
        
        for i, article in enumerate(articles, 1):
            quantity = article.get('quantity', 0) or 0
            unit_price = article.get('unit_price', 0) or 0
            line_total = quantity * unit_price if quantity and unit_price else 0
            total_value += line_total
            
            article_rows.append(html.Div([
                html.Div([
                    html.Div([
                        html.Strong(f"Article {i}"),
                        html.Button(
                            "✖",
                            id={'type': 'delete-article-button', 'index': i},
                            className="delete-article-button",
                            title=f"Supprimer l'article {i}",
                            n_clicks=0
                        )
                    ], className="article-header"),
                    html.Div([
                        html.Span("Code: ", className="label-small"),
                        dcc.Input(
                            id={'type': 'editable-article', 'index': i, 'field': 'code'},
                            value=article.get('code', ''),
                            className='editable-input-small',
                            placeholder='Code article'
                        )
                    ], className="side-by-side"),
                    html.Div([
                        html.Span("Description: ", className="label-small"),
                        dcc.Textarea(
                            id={'type': 'editable-article', 'index': i, 'field': 'description'},
                            value=article.get('description', ''),
                            className='editable-textarea-small',
                            placeholder='Description de l\'article'
                        )
                    ], className="side-by-side")
                ], className="article-info"),
                html.Div([
                    html.Div([
                        html.Span("Quantité: ", className="label-small"),
                        dcc.Input(
                            id={'type': 'editable-article', 'index': i, 'field': 'quantity'},
                            value=quantity,
                            type='number',
                            className='editable-input-small',
                            placeholder='0'
                        )
                    ], className="side-by-side"),
                    html.Div([
                        html.Span("Unité: ", className="label-small"),
                        dcc.Input(
                            id={'type': 'editable-article', 'index': i, 'field': 'unit'},
                            value=article.get('unit', ''),
                            className='editable-input-small',
                            placeholder='unité'
                        )
                    ], className="side-by-side"),
                    html.Div([
                        html.Span("Prix unitaire: ", className="label-small"),
                        dcc.Input(
                            id={'type': 'editable-article', 'index': i, 'field': 'unit_price'},
                            value=unit_price,
                            type='number',
                            step=0.01,
                            className='editable-input-small',
                            placeholder='0.00'
                        )
                    ], className="side-by-side"),
                    html.Div([
                        html.Span("Total ligne: ", className="label-small"),
                        html.Span(f"{line_total:.2f}€" if line_total else "0.00€", 
                                className="value-small total-line")
                    ])
                ], className="article-numbers")
            ], className="article-row editable-article-row", id=f"article-row-{i}"))
        
        articles_content = html.Div([
            articles_header,
            html.Div(article_rows, id="articles-list"),
            html.Div([
                html.Strong([
                    html.Span("Total estimé: ", className="label"),
                    html.Span(f"{total_value:.2f}€", className="total-value")
                ])
            ], className="total-section")
        ], className="section exception2")
    else:
        # If no articles, show empty state
        articles_content = html.Div([
            articles_header,
            html.Div([
                html.P("Aucun article pour le moment.", className="empty-articles-message"),
                html.P("Cliquez sur 'Ajouter un article' pour commencer.", className="empty-articles-help")
            ], className="empty-articles-state", id="articles-list"),
            html.Div([
                html.Strong([
                    html.Span("Total estimé: ", className="label"),
                    html.Span("0.00€", className="total-value")
                ])
            ], className="total-section")
        ], className="section exception2")
    
    content.append(articles_content)
    
    return html.Div(content, className="human-readable-content")