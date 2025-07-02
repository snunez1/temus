"""
Utility functions for the Temus Wind Forecasting project.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_to_parquet(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    create_dirs: bool = True,
    compression: str = 'snappy',
    **kwargs
) -> bool:
    """
    Save DataFrame to parquet file with standard settings for the project.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    filepath : str or Path
        Path to save the parquet file
    create_dirs : bool, default=True
        Whether to create parent directories if they don't exist
    compression : str, default='snappy'
        Compression algorithm to use
    **kwargs
        Additional arguments passed to pd.DataFrame.to_parquet()
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    >>> save_to_parquet(df, 'data/processed/sample.parquet')
    True
    """
    try:
        filepath = Path(filepath)
        
        # Create directories if needed
        if create_dirs:
            filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Default parameters for consistent saving
        default_params = {
            'index': False,
            'compression': compression,
            'engine': 'pyarrow'
        }
        
        # Update with any user-provided parameters
        default_params.update(kwargs)
        
        # Save the DataFrame
        df.to_parquet(filepath, **default_params)
        
        # Log success with file size
        file_size = filepath.stat().st_size
        logger.info(f"Saved {len(df):,} rows to {filepath} ({file_size:,} bytes)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save DataFrame to {filepath}: {e}")
        return False


def load_from_parquet(
    filepath: Union[str, Path],
    **kwargs
) -> Optional[pd.DataFrame]:
    """
    Load DataFrame from parquet file with error handling.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the parquet file
    **kwargs
        Additional arguments passed to pd.read_parquet()
    
    Returns:
    --------
    pd.DataFrame or None
        Loaded DataFrame, or None if loading failed
    
    Examples:
    ---------
    >>> df = load_from_parquet('data/processed/sample.parquet')
    >>> print(df.shape)
    (3, 2)
    """
    try:
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File does not exist: {filepath}")
            return None
        
        # Default parameters
        default_params = {
            'engine': 'pyarrow'
        }
        
        # Update with user parameters
        default_params.update(kwargs)
        
        # Load the DataFrame
        df = pd.read_parquet(filepath, **default_params)
        
        # Log success
        logger.info(f"Loaded {len(df):,} rows from {filepath}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load DataFrame from {filepath}: {e}")
        return None


def save_results_dict(
    results: Dict[str, Any],
    filepath: Union[str, Path],
    create_dirs: bool = True
) -> bool:
    """
    Save results dictionary as a single-row DataFrame to parquet.
    Useful for saving analysis results between notebooks.
    
    Parameters:
    -----------
    results : dict
        Dictionary of results to save
    filepath : str or Path
        Path to save the parquet file
    create_dirs : bool, default=True
        Whether to create parent directories
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> results = {'accuracy': 0.95, 'model': 'XGBoost', 'features': ['wind_speed', 'direction']}
    >>> save_results_dict(results, 'outputs/model_results.parquet')
    True
    """
    try:
        # Convert dict to single-row DataFrame
        results_df = pd.DataFrame([results])
        
        # Use the main save function
        return save_to_parquet(results_df, filepath, create_dirs=create_dirs)
        
    except Exception as e:
        logger.error(f"Failed to save results dict: {e}")
        return False


def get_project_paths() -> Dict[str, Path]:
    """
    Get standard project paths for consistent file organization.
    
    Returns:
    --------
    dict
        Dictionary of project paths
    """
    # Get project root (assumes this file is in src/)
    project_root = Path(__file__).parent.parent
    
    paths = {
        'root': project_root,
        'data_raw': project_root / 'data' / 'raw',
        'data_processed': project_root / 'data' / 'processed',
        'data_intermediate': project_root / 'data' / 'intermediate',
        'outputs': project_root / 'outputs',
        'figures': project_root / 'notebooks' / 'outputs' / 'figures',
        'results': project_root / 'outputs' / 'results',
        'models': project_root / 'models',
        'notebooks': project_root / 'notebooks',
        'src': project_root / 'src'
    }
    
    return paths


def ensure_pyarrow():
    """
    Ensure pyarrow is available for parquet operations.
    """
    try:
        import pyarrow
        logger.info(f"PyArrow {pyarrow.__version__} is available")
        return True
    except ImportError:
        logger.warning("PyArrow not found. Installing...")
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyarrow"])
            import pyarrow
            logger.info(f"PyArrow {pyarrow.__version__} installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to install PyArrow: {e}")
            return False


def save_figure(
    fig,
    filename: str,
    subdir: str = '',
    dpi: int = 300,
    bbox_inches: str = 'tight',
    format: str = 'png',
    create_dirs: bool = True,
    **kwargs
) -> bool:
    """
    Save a matplotlib figure to /notebooks/outputs/figures with consistent settings.
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure to save
    filename : str
        Name of the file (without extension)
    subdir : str, default=''
        Optional subdirectory within notebooks/outputs/figures
    dpi : int, default=300
        Resolution for the saved figure
    bbox_inches : str, default='tight'
        Bounding box setting for the figure
    format : str, default='png'
        File format for saving
    create_dirs : bool, default=True
        Whether to create directories if they don't exist
    **kwargs
        Additional arguments passed to fig.savefig()
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 2])
    >>> save_figure(fig, 'sample_plot')
    True
    """
    try:
        # Get project paths
        paths = get_project_paths()
        
        # Create save directory - always use notebooks/outputs/figures
        if subdir:
            save_dir = paths['figures'] / subdir
        else:
            save_dir = paths['figures']
            
        if create_dirs:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct full filepath
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
        filepath = save_dir / filename
        
        # Save the figure
        fig.savefig(
            filepath, 
            dpi=dpi, 
            bbox_inches=bbox_inches, 
            format=format,
            **kwargs
        )
        
        logger.info(f"Figure saved: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save figure {filename}: {e}")
        return False


def create_and_save_figure(filename=None, figsize=(12, 8), dpi=300, 
                                   format='png', save_to_outputs=True, show_figure=True):
    """
    Enhanced decorator that addresses scope issues and provides more flexibility.
    
    This improved version:
    - Requires all data to be passed as explicit parameters
    - Provides configurable saving and display options
    - Includes robust error handling
    - Avoids closure/scope issues that plagued the original decorator
    
    Parameters:
    -----------
    filename : str, optional
        Custom filename (auto-generated from function name if None)
    figsize : tuple, default=(12, 8)
        Figure size tuple (width, height)
    dpi : int, default=300
        Resolution for saved figures
    format : str, default='png'
        File format ('png', 'pdf', 'svg')
    save_to_outputs : bool, default=True
        Whether to save figure to outputs directory
    show_figure : bool, default=True
        Whether to display figure in notebook
        
    Returns:
    --------
    function
        Decorated function that handles figure creation, saving, and display
        
    Examples:
    ---------
    # Basic usage with automatic filename
    @create_and_save_figure()
    def plot_analysis(data, results, ax=None):
        ax.plot(data.index, data.values)
        return ax
        
    # Custom configuration
    @create_and_save_figure(filename='custom_plot', figsize=(16, 10), dpi=150)
    def plot_detailed_analysis(data, parameters, ax=None):
        # All required data passed as parameters - no scope issues
        return create_complex_plot(data, parameters, ax)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import matplotlib.pyplot as plt
            from pathlib import Path
            
            # Determine filename
            save_filename = filename or func.__name__.replace('plot_', '').replace('_', '_')
            
            # Extract data parameter if provided (fix for DataFrame ambiguous truth value)
            data = kwargs.get('data')
            if data is None and args:
                data = args[0]
            
            # Create figure if not provided in kwargs
            if 'ax' not in kwargs or kwargs['ax'] is None:
                fig, ax = plt.subplots(figsize=figsize)
                kwargs['ax'] = ax
            else:
                ax = kwargs['ax']
                fig = ax.figure
            
            try:
                # Call the plotting function with all required data passed as parameters
                result = func(*args, **kwargs)
                
                # Apply consistent styling
                if not ax.get_title():
                    ax.set_title(func.__name__.replace('_', ' ').title(), 
                               fontsize=14, fontweight='bold')
                
                # Save figure if requested
                if save_to_outputs and save_filename:
                    # Get project paths and ensure figures directory exists
                    paths = get_project_paths()
                    figures_dir = paths['figures']
                    figures_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save with specified format and DPI
                    save_path = figures_dir / f"{save_filename}.{format}"
                    fig.savefig(save_path, dpi=dpi, bbox_inches='tight', 
                               facecolor='white', edgecolor='none')
                    logger.info(f"Figure saved: {save_path}")
                
                # Display figure if requested
                if show_figure:
                    plt.tight_layout()
                    plt.show()
                
                return result
                
            except Exception as e:
                logger.error(f"Error in plotting function {func.__name__}: {e}")
                # Show empty plot with error message
                ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12, color='red')
                ax.set_title(f'Error in {func.__name__}', fontsize=14, color='red')
                if show_figure:
                    plt.show()
                return None
                
        return wrapper
    return decorator


def ensure_figures_directory() -> Path:
    """
    Ensure the figures directory exists and return its path.
    
    Returns:
    --------
    Path
        Path to the figures directory
    """
    paths = get_project_paths()
    figures_dir = paths['figures']  # Now points to notebooks/outputs/figures
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    subdir: str = '',
    create_dirs: bool = True,
    **kwargs
) -> bool:
    """
    Save DataFrame to the data/processed directory with consistent settings.
    
    This function ensures all processed datasets are saved to the correct
    project-level data/processed directory, regardless of notebook location.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    filename : str
        Name of the file (with or without .parquet extension)
    subdir : str, default=''
        Optional subdirectory within data/processed
    create_dirs : bool, default=True
        Whether to create directories if they don't exist
    **kwargs
        Additional arguments passed to save_to_parquet()
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    >>> save_processed_data(df, 'clean_data')
    True
    >>> save_processed_data(df, 'features.parquet', subdir='features')
    True
    """
    try:
        # Get project paths to ensure absolute paths
        paths = get_project_paths()
        
        # Ensure filename has .parquet extension
        if not filename.endswith('.parquet'):
            filename = f"{filename}.parquet"
        
        # Create save directory path
        if subdir:
            save_dir = paths['data_processed'] / subdir
        else:
            save_dir = paths['data_processed']
        
        # Create directory if needed
        if create_dirs:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct full filepath
        filepath = save_dir / filename
        
        # Ensure we're using absolute path
        filepath = filepath.resolve()
        
        # Save the DataFrame
        success = save_to_parquet(df, filepath, create_dirs=False, **kwargs)
        
        if success:
            logger.info(f"Processed data saved: {filepath}")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to save processed data {filename}: {e}")
        return False


def save_analysis_results(
    results: Dict[str, Any],
    filename: str,
    notebook_name: str = None,
    to_data_dir: bool = True,
    **kwargs
) -> bool:
    """
    Save analysis results as parquet files to /data/processed directory.
    
    Parameters:
    -----------
    results : dict
        Dictionary of analysis results
    filename : str
        Base filename (without extension)
    notebook_name : str, optional
        Name of the notebook for prefixing (e.g., '01_data_foundation')
    to_data_dir : bool, default=True
        If True, save to data/processed; if False, save to outputs
    **kwargs
        Additional arguments passed to save_results_dict()
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> results = {'accuracy': 0.95, 'timestamp': '2024-01-15'}
    >>> save_analysis_results(results, 'model_evaluation', '03_modeling')
    True
    """
    try:
        # Get project paths
        paths = get_project_paths()
        
        # Create filename with notebook prefix if provided
        if notebook_name:
            if not filename.startswith(notebook_name):
                filename = f"{notebook_name}_{filename}"
        
        # Ensure .parquet extension
        if not filename.endswith('.parquet'):
            filename = f"{filename}.parquet"
        
        # Choose directory based on parameter
        if to_data_dir:
            filepath = paths['data_processed'] / filename
        else:
            filepath = paths['outputs'] / filename
        
        # Ensure absolute path
        filepath = filepath.resolve()
        
        # Save results
        success = save_results_dict(results, filepath, **kwargs)
        
        if success:
            logger.info(f"Analysis results saved: {filepath}")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to save analysis results {filename}: {e}")
        return False


def ensure_data_directories() -> Dict[str, Path]:
    """
    Ensure all standard data directories exist and return their absolute paths.
    Following copilot-instructions.md: data files go to /data/processed and /data/intermediate,
    visualizations go to /notebooks/outputs/figures. Do not create /outputs for data files.
    
    Returns:
    --------
    dict
        Dictionary with directory paths
    """
    try:
        paths = get_project_paths()
        
        # Standard directories to ensure exist (excluding /outputs for data files)
        directories = {
            'data_raw': paths['data_raw'],
            'data_processed': paths['data_processed'], 
            'data_intermediate': paths['data_intermediate'],
            'figures': paths['figures'],  # /notebooks/outputs/figures for PNG files
            'models': paths['models']
        }
        
        # Create all directories
        for name, path in directories.items():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")
        
        return directories
        
    except Exception as e:
        logger.error(f"Failed to create data directories: {e}")
        return {}


def save_intermediate_data(
    df: pd.DataFrame,
    filename: str,
    subdir: str = '',
    create_dirs: bool = True,
    **kwargs
) -> bool:
    """
    Save DataFrame to the data/intermediate directory for intermediate processing steps.
    
    This function saves datasets that are processed but not final outputs,
    such as cleaned data before feature engineering or temporary analysis results.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    filename : str
        Name of the file (with or without .parquet extension)
    subdir : str, default=''
        Optional subdirectory within data/intermediate
    create_dirs : bool, default=True
        Whether to create directories if they don't exist
    **kwargs
        Additional arguments passed to save_to_parquet()
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    
    Examples:
    ---------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    >>> save_intermediate_data(df, 'temp_analysis')
    True
    >>> save_intermediate_data(df, 'cleaned.parquet', subdir='preprocessing')
    True
    """
    try:
        # Get project paths to ensure absolute paths
        paths = get_project_paths()
        
        # Ensure filename has .parquet extension
        if not filename.endswith('.parquet'):
            filename = f"{filename}.parquet"
        
        # Create save directory path
        if subdir:
            save_dir = paths['data_intermediate'] / subdir
        else:
            save_dir = paths['data_intermediate']
        
        # Create directory if needed
        if create_dirs:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct full filepath
        filepath = save_dir / filename
        
        # Ensure we're using absolute path
        filepath = filepath.resolve()
        
        # Save the DataFrame
        success = save_to_parquet(df, filepath, create_dirs=False, **kwargs)
        
        if success:
            logger.info(f"Intermediate data saved: {filepath}")
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to save intermediate data {filename}: {e}")
        return False


class AnalysisVisualizer:
    """
    Class-based approach for managing complex plotting state and data dependencies.
    
    This addresses scope issues by encapsulating data and methods together,
    providing a robust framework for complex visualizations that require
    multiple data sources and state management.
    
    Attributes:
    -----------
    data : pd.DataFrame
        Primary analysis dataset
    results_dict : dict
        Dictionary containing analysis results
    figures_created : list
        List of figures created during analysis
    config : dict
        Configuration settings for visualizations
        
    Examples:
    ---------
    # Initialize with data and results
    visualizer = AnalysisVisualizer(analysis_data, results_dict)
    
    # Create visualizations with encapsulated data
    visualizer.plot_temporal_patterns()
    visualizer.plot_correlations()
    
    # Get summary of work performed
    summary = visualizer.get_analysis_summary()
    """
    
    def __init__(self, data, results_dict=None, config=None):
        """
        Initialize the visualizer with data and configuration.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Primary analysis dataset
        results_dict : dict, optional
            Dictionary containing analysis results
        config : dict, optional
            Configuration settings for visualizations
        """
        self.data = data
        self.results_dict = results_dict or {}
        self.figures_created = []
        self.config = config or {
            'figsize': (12, 8),
            'dpi': 300,
            'format': 'png',
            'style': 'default'
        }
    
    @create_and_save_figure(filename='visualizer_demo', show_figure=True)
    def plot_data_overview(self, ax=None):
        """Example method showing encapsulated plotting"""
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=self.config['figsize'])
        
        # Use self.data - no scope issues
        if hasattr(self.data, 'columns') and 'POWER' in self.data.columns:
            power_data = self.data['POWER'].dropna()
            ax.hist(power_data, bins=50, alpha=0.7, edgecolor='black')
            ax.set_xlabel('Power Generation (MW)')
            ax.set_ylabel('Frequency')
            ax.set_title('Power Generation Distribution')
        else:
            ax.text(0.5, 0.5, 'No power data available', 
                   ha='center', va='center', transform=ax.transAxes)
        
        self.figures_created.append('data_overview')
        return ax
    
    def add_results(self, key, results):
        """Add analysis results to the results dictionary"""
        self.results_dict[key] = results
    
    def get_analysis_summary(self):
        """Return summary of analysis performed"""
        return {
            'data_shape': self.data.shape if hasattr(self.data, 'shape') else None,
            'figures_created': self.figures_created,
            'results_available': list(self.results_dict.keys()),
            'config': self.config
        }
    
    def update_config(self, **kwargs):
        """Update visualization configuration"""
        self.config.update(kwargs)


# Initialize pyarrow on import
ensure_pyarrow()
