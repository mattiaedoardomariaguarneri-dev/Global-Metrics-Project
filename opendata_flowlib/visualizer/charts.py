import logging
from typing import Any, List, Literal, Optional, Union

import pandas as pd

logger = logging.getLogger("opendata_flowlib.visualizer.charts")

def plot_bar(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None,
    backend: Literal["plotly", "matplotlib"] = "plotly"
) -> Any:
    """Crea un grafico a barre.

    Args:
        df: DataFrame.
        x: Colonna per asse X.
        y: Colonna per asse Y.
        title: Titolo del grafico.
        color: Colonna per colore.
        backend: Backend da usare ('plotly' o 'matplotlib').

    Returns:
        Oggetto Figure del backend selezionato.
    """
    logger.info(f"Plotting bar chart: x={x}, y={y}, backend={backend}")
    if backend == "plotly":
        import plotly.express as px
        fig = px.bar(df, x=x, y=y, title=title, color=color)
        return fig
    else:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        if color:
            # Semplificazione per matplotlib: iteriamo sui gruppi se c'è colore
            for name, group in df.groupby(color):
                ax.bar(group[x], group[y], label=name)
            ax.legend()
        else:
            ax.bar(df[x], df[y])
        ax.set_title(title)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        return fig

def plot_line(
    df: pd.DataFrame,
    x: str,
    y: Union[str, List[str]],
    title: str = "",
    backend: Literal["plotly", "matplotlib"] = "plotly"
) -> Any:
    """Crea un grafico a linee."""
    logger.info(f"Plotting line chart: x={x}, y={y}, backend={backend}")
    if backend == "plotly":
        import plotly.express as px
        fig = px.line(df, x=x, y=y, title=title)
        return fig
    else:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        if isinstance(y, list):
            for col in y:
                ax.plot(df[x], df[col], label=col)
            ax.legend()
        else:
            ax.plot(df[x], df[y])
        ax.set_title(title)
        ax.set_xlabel(x)
        ax.set_ylabel(str(y))
        return fig

def plot_scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    backend: Literal["plotly", "matplotlib"] = "plotly"
) -> Any:
    """Crea uno scatter plot."""
    logger.info(f"Plotting scatter chart: x={x}, y={y}, hue={hue}, backend={backend}")
    if backend == "plotly":
        import plotly.express as px
        fig = px.scatter(df, x=x, y=y, color=hue, title=f"Scatter: {x} vs {y}")
        return fig
    else:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        if hue:
            for name, group in df.groupby(hue):
                ax.scatter(group[x], group[y], label=name)
            ax.legend()
        else:
            ax.scatter(df[x], df[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        return fig

def plot_histogram(
    df: pd.DataFrame,
    column: str,
    bins: int = 30,
    backend: Literal["plotly", "matplotlib"] = "plotly"
) -> Any:
    """Crea un istogramma."""
    logger.info(f"Plotting histogram: column={column}, bins={bins}, backend={backend}")
    if backend == "plotly":
        import plotly.express as px
        fig = px.histogram(df, x=column, nbins=bins, title=f"Histogram of {column}")
        return fig
    else:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.hist(df[column].dropna(), bins=bins)
        ax.set_title(f"Histogram of {column}")
        ax.set_xlabel(column)
        return fig

def plot_heatmap(
    df: pd.DataFrame,
    title: str = "",
    backend: Literal["plotly", "matplotlib"] = "plotly"
) -> Any:
    """Crea una mappa di calore (matrice di correlazione)."""
    logger.info(f"Plotting heatmap: backend={backend}")
    # Calculate correlation only on numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()
    
    if backend == "plotly":
        import plotly.express as px
        fig = px.imshow(corr, title=title, text_auto=True)
        return fig
    else:
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots()
        cax = ax.matshow(corr, cmap='coolwarm')
        fig.colorbar(cax)
        ax.set_xticks(np.arange(len(corr.columns)))
        ax.set_yticks(np.arange(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=90)
        ax.set_yticklabels(corr.columns)
        ax.set_title(title, pad=20)
        return fig
