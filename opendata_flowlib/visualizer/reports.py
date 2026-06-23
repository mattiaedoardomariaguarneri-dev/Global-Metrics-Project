import logging
from typing import Any, List

logger = logging.getLogger("opendata_flowlib.visualizer.reports")

def export_html(figures: List[Any], path: str, title: str = "Report") -> None:
    """Esporta una lista di figure in un file HTML unico.

    Supporta sia plotly che matplotlib figures.

    Args:
        figures: Lista di oggetti Figure.
        path: Percorso del file HTML di output.
        title: Titolo del report HTML.
    """
    logger.info(f"Exporting {len(figures)} figures to HTML: {path}")
    
    html_content = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: sans-serif; margin: 40px; }}
            .chart-container {{ margin-bottom: 50px; text-align: center; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>{title}</h1>
    """
    
    for i, fig in enumerate(figures):
        html_content += f'<div class="chart-container">\n'
        
        # Check if plotly figure
        if hasattr(fig, 'to_html'):
            # Convert plotly to html div
            div = fig.to_html(full_html=False, include_plotlyjs=False)
            html_content += div
        # Check if matplotlib figure
        elif hasattr(fig, 'savefig'):
            import base64
            from io import BytesIO
            
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            html_content += f'<img src="data:image/png;base64,{data}"/>'
            
        html_content += f'</div>\n'
        
    html_content += """
    </body>
    </html>
    """
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def export_pdf(figures: List[Any], path: str, title: str = "Report") -> None:
    """Esporta una lista di figure in un file PDF unico.

    Args:
        figures: Lista di oggetti Figure.
        path: Percorso del file PDF di output.
        title: Titolo del report PDF.
    """
    logger.info(f"Exporting {len(figures)} figures to PDF: {path}")
    
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    with PdfPages(path) as pdf:
        for fig in figures:
            if hasattr(fig, 'write_image'):
                # It's a plotly figure, convert to image then to matplotlib to save
                import io
                import plotly.io as pio
                from PIL import Image
                
                img_bytes = pio.to_image(fig, format='png')
                img = Image.open(io.BytesIO(img_bytes))
                
                # Create a new matplotlib figure for this image
                mpl_fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(img)
                ax.axis('off')
                pdf.savefig(mpl_fig)
                plt.close(mpl_fig)
            elif hasattr(fig, 'savefig'):
                # It's already matplotlib
                pdf.savefig(fig)
