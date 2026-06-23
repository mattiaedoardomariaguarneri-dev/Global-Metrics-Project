import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import pandas as pd
import yaml

logger = logging.getLogger("opendata_flowlib.pipeline.pipeline")

@dataclass
class StepLog:
    step_name: str
    duration_ms: float
    shape_in: Tuple[int, int]
    shape_out: Tuple[int, int]

@dataclass
class PipelineResult:
    df: pd.DataFrame
    figures: List[Any]
    steps_log: List[StepLog]
    errors: List[Exception]

class Pipeline:
    """Orchestratore di una pipeline di dati con fluent interface."""
    
    def __init__(self, on_error: Literal["raise", "skip", "warn"] = "raise"):
        self.on_error = on_error
        self.steps: List[Dict[str, Any]] = []
        self._df: Optional[pd.DataFrame] = None
        self._figures: List[Any] = []
        self._steps_log: List[StepLog] = []
        self._errors: List[Exception] = []

    def read(self, reader_fn: Callable, *args, **kwargs) -> "Pipeline":
        """Registra uno step di lettura. Il primo step della pipeline."""
        self.steps.append({
            "type": "read",
            "fn": reader_fn,
            "args": args,
            "kwargs": kwargs
        })
        return self

    def clean(self, cleaner_fn: Callable, **kwargs) -> "Pipeline":
        """Registra uno step di pulizia."""
        self.steps.append({
            "type": "clean",
            "fn": cleaner_fn,
            "args": (),
            "kwargs": kwargs
        })
        return self

    def process(self, processor_fn: Callable, **kwargs) -> "Pipeline":
        """Registra uno step di elaborazione/trasformazione."""
        self.steps.append({
            "type": "process",
            "fn": processor_fn,
            "args": (),
            "kwargs": kwargs
        })
        return self

    def visualize(self, viz_fn: Callable, **kwargs) -> "Pipeline":
        """Registra uno step di visualizzazione."""
        self.steps.append({
            "type": "visualize",
            "fn": viz_fn,
            "args": (),
            "kwargs": kwargs
        })
        return self

    def run(self) -> PipelineResult:
        """Esegue tutti gli step registrati in ordine e restituisce il risultato."""
        self._df = None
        self._figures = []
        self._steps_log = []
        self._errors = []
        
        for step_info in self.steps:
            fn = step_info["fn"]
            step_type = step_info["type"]
            args = step_info["args"]
            kwargs = step_info["kwargs"]
            step_name = fn.__name__ if hasattr(fn, '__name__') else str(fn)
            
            shape_in = self._df.shape if self._df is not None else (0, 0)
            start_time = time.perf_counter()
            
            try:
                if step_type == "read":
                    self._df = fn(*args, **kwargs)
                elif step_type == "visualize":
                    fig = fn(self._df, *args, **kwargs)
                    self._figures.append(fig)
                else:  # clean, process
                    self._df = fn(self._df, *args, **kwargs)
                    
                duration_ms = (time.perf_counter() - start_time) * 1000
                shape_out = self._df.shape if self._df is not None else (0, 0)
                
                log_entry = StepLog(
                    step_name=step_name,
                    duration_ms=duration_ms,
                    shape_in=shape_in,
                    shape_out=shape_out
                )
                self._steps_log.append(log_entry)
                
                logger.info(f"step '{step_name}': {shape_in} -> {shape_out} ({duration_ms:.1f} ms)")
                
            except Exception as e:
                self._errors.append(e)
                if self.on_error == "raise":
                    raise e
                elif self.on_error == "warn":
                    logger.warning(f"Error in step '{step_name}': {e}. Continuing pipeline.")
                elif self.on_error == "skip":
                    logger.info(f"Skipping step '{step_name}' due to error: {e}")
                    
        final_shape = self._df.shape if self._df is not None else (0, 0)
        logger.info(f"Pipeline complete — final shape: {final_shape}")
        
        return PipelineResult(
            df=self._df,
            figures=self._figures,
            steps_log=self._steps_log,
            errors=self._errors
        )

    def to_yaml(self, path: str) -> None:
        """Serializza la pipeline su file YAML (nome moduli e kwargs base)."""
        yaml_steps = []
        for step in self.steps:
            fn = step["fn"]
            fn_name = f"{fn.__module__}.{fn.__name__}" if hasattr(fn, '__module__') and hasattr(fn, '__name__') else str(fn)
            # Remove non-serializable args from kwargs
            safe_kwargs = {k: v for k, v in step["kwargs"].items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
            yaml_steps.append({
                "type": step["type"],
                "function": fn_name,
                "kwargs": safe_kwargs
            })
            
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump({"steps": yaml_steps, "on_error": self.on_error}, f)

    @classmethod
    def from_yaml(cls, path: str) -> "Pipeline":
        """Carica una pipeline da file YAML."""
        import importlib
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        pipeline = cls(on_error=data.get("on_error", "raise"))
        
        for step_data in data.get("steps", []):
            module_name, fn_name = step_data["function"].rsplit(".", 1)
            module = importlib.import_module(module_name)
            fn = getattr(module, fn_name)
            
            step_type = step_data["type"]
            kwargs = step_data.get("kwargs", {})
            
            if step_type == "read":
                pipeline.read(fn, **kwargs)
            elif step_type == "clean":
                pipeline.clean(fn, **kwargs)
            elif step_type == "process":
                pipeline.process(fn, **kwargs)
            elif step_type == "visualize":
                pipeline.visualize(fn, **kwargs)
                
        return pipeline

def step(fn: Callable, *args, **kwargs) -> Callable:
    """Wrappa una funzione con i suoi argomenti per la composizione."""
    def wrapper(df: pd.DataFrame) -> pd.DataFrame:
        return fn(df, *args, **kwargs)
    return wrapper

def compose(*steps) -> Callable:
    """Compone più step in una pipeline funzionale."""
    def wrapper(df: pd.DataFrame) -> pd.DataFrame:
        result = df
        for step_fn in steps:
            result = step_fn(result)
        return result
    return wrapper
