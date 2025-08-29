import dash
from dash import Input, Output, State
import fitz  # PyMuPDF
import base64
import io
from PIL import Image

def _convert_pdf_to_image(contents, page_num=0):
    """Convert PDF to image using PyMuPDF (fitz)"""
    try:
        # Extract base64 data from the data URL
        content_type, content_string = contents.split(',')
        pdf_data = base64.b64decode(content_string)
        
        # Open PDF with fitz
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        
        # Get the specified page (default to first page)
        if page_num >= len(pdf_document):
            page_num = 0
        
        page = pdf_document.load_page(page_num)
        
        # Render page to image (higher DPI for better quality)
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Convert back to base64 for display
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        pdf_document.close()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return None

def _is_pdf_file(filename):
    """Check if the uploaded file is a PDF"""
    if filename:
        return filename.lower().endswith('.pdf')
    return False

# Handle initial upload
def _register_handle_initial_upload(app):
    @app.callback(
        Output('stored-image', 'data'),
        Output('image-display-row', 'style'),
        Output('initial-upload-row', 'style'),
        Input('initial-upload', 'contents'),
        State('initial-upload', 'filename')
    )
    def handle_initial_upload(contents, filename):
        if contents:
            processed_contents = contents
            
            # If it's a PDF, convert to image
            if _is_pdf_file(filename):
                converted_image = _convert_pdf_to_image(contents)
                if converted_image:
                    processed_contents = converted_image
                    # Update filename to indicate conversion
                    filename = f"{filename} (converted to image)"
                else:
                    # If conversion fails, return no update
                    return dash.no_update, dash.no_update, dash.no_update
            
            # Store the processed image data globally for streaming use
            app.current_image_data = processed_contents
            return {'src': processed_contents, 'filename': filename}, {'display': 'block'}, {'display': 'none'}
        return dash.no_update, dash.no_update, dash.no_update

# Handle overlay upload
def _register_handle_overlay_upload(app):
    @app.callback(
        Output('stored-image', 'data', allow_duplicate=True),
        Input('overlay-upload', 'contents'),
        State('overlay-upload', 'filename'),
        prevent_initial_call=True
    )
    def handle_overlay_upload(contents, filename):
        if contents:
            processed_contents = contents
            
            # If it's a PDF, convert to image
            if _is_pdf_file(filename):
                converted_image = _convert_pdf_to_image(contents)
                if converted_image:
                    processed_contents = converted_image
                    # Update filename to indicate conversion
                    filename = f"{filename} (converted to image)"
                else:
                    # If conversion fails, return no update
                    return dash.no_update
            
            # Update the global image data
            app.current_image_data = processed_contents
            return {'src': processed_contents, 'filename': filename}
        return dash.no_update

# Update displayed image and overlay text
def _register_update_display(app):
    @app.callback(
        Output('displayed-image', 'src'),
        Output('overlay-div', 'children'),
        Input('stored-image', 'data')
    )
    def update_display(data):
        if data:
            return data['src'], f"Drop to replace: {data['filename']}"
        return None, "Drop new image or PDF to replace"