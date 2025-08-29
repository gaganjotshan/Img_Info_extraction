YAML_EXTRACTION_PROMPT = """system: |
  You are a French document extraction expert. Analyze this delivery note and output ALL data as YAML with these principles:
  1. Use flat key-value pairs with descriptive English keys
  2. Preserve EXACT original French text values, including addresses, company names, descriptions, and any other textual information present in the document
  3. Convert all numeric values: "1.234,56" → 1234.56
  4. Never invent data - use "null" for missing fields. If a field is present but empty, use an empty string `""` instead of `null`
  5. Group related items using lists when logical
  6. Capture EVERY data point including:
     - Header/footer text
     - Table headers and values
  7. SPECIAL COMPANY RULES:
     - "Eiffage" is ALWAYS the recipient (client)
     - The other mentioned company is ALWAYS the supplier
     - The supplier might list two addresses: their corporate headquarters and the specific branch handling the delivery. If the supplier has two addresses, represent them as a list under the `supplier_addresses` key
     - Ignore legal disclaimers and safety warnings
  10. Use comments in the YAML to explain any non-obvious decisions or assumptions made during the extraction process

  Required YAML structure:
  ```yaml
  document_type: "Bon de Livraison"
  extracted_fields:
    supplier_name: 
      - value: "Exact French supplier text" 
    client_name: 
      - value: "Exact French Eiffage text"
    # Add other fields (dates, amounts, etc.)
  line_items:
    - item_code: "value"
      description: "value"
      quantity: 123.45
      # ...other columns
  raw_text_segments:
    - "Full text block 1"
    - "Full text block 2"
    - ..."""


JSON_EXTRACTION_PROMPT = f"""Tu es un expert en extraction de données de bons de livraison français. 
Le texte suivant est au format yaml structuré converti depuis une image de bon de livraison.
Extrais les informations et retourne UNIQUEMENT du JSON valide dans ce format:
{{
  "bl_number": "numero du BL",
  "order_number": "numero commande (C4*, C5*, C8*, C2*)",
  "supplier": {{
    "name": "nom fournisseur",
    "siren": "9 chiffres",
    "siret": "14 chiffres", 
    "address": "adresse complete"
  }},
  "articles": [
    {{
      "code": "code article",
      "description": "description",
      "quantity": 20.0,
      "unit": "unité",
      "unit_price": 15.50
    }}
  ]
}}
Instructions:
- Analyse le contenu yaml structuré
- Utilise les tableaux yaml pour identifier les articles
- Si une information manque, utilise null
CONTENU YAML À ANALYSER:
"""