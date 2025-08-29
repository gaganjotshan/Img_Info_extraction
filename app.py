from dash import Dash, Input, Output
from src.layout import create_layout
from src.callbacks import register_callbacks

app = Dash(__name__, assets_folder='assets')
app.title = "Eiffage BL"
app.current_image_data = None
app.extracted_json_data = None

app.layout = create_layout()
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8060)