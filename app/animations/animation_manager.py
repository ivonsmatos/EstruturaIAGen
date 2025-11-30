"""
Animation Manager for Plotly Charts
===================================

Provides smooth animations, transitions, and interactive effects for dashboard charts.
Supports frame-based animations, progressive updates, and custom animation sequences.

Version: 3.0.0
Author: AI Dashboard Team
License: MIT
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import logging
import json
from enum import Enum
from datetime import datetime, timedelta
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class AnimationType(Enum):
    """Enumeration of available animation types"""
    SLIDE = "slide"
    FADE = "fade"
    ZOOM = "zoom"
    SCATTER = "scatter"
    BAR_RACE = "bar_race"
    LINE_DRAW = "line_draw"
    BUBBLE = "bubble"
    GRADIENT = "gradient"


class TransitionType(Enum):
    """Enumeration of transition types"""
    LINEAR = "linear"
    QUAD = "quad"
    CUBIC = "cubic"
    ELASTIC = "elastic"
    BOUNCE = "bounce"


@dataclass
class AnimationConfig:
    """Configuration for chart animations"""
    animation_type: AnimationType = AnimationType.SLIDE
    duration: int = 500  # milliseconds
    delay: int = 100  # milliseconds between frames
    transition_type: TransitionType = TransitionType.CUBIC
    frame_count: int = 20
    redraw: bool = True
    show_progress: bool = True


class PlotlyAnimationManager:
    """
    Manages advanced animations and transitions for Plotly charts.
    
    Features:
    - Frame-based animations
    - Progressive data updates
    - Smooth transitions
    - Multiple animation types
    - Performance optimization
    
    Example:
        >>> manager = PlotlyAnimationManager()
        >>> fig = manager.animate_bar_chart(
        ...     data=df,
        ...     x_col='category',
        ...     y_col='value',
        ...     animation_config=AnimationConfig(
        ...         animation_type=AnimationType.BAR_RACE,
        ...         duration=800
        ...     )
        ... )
    """
    
    def __init__(self):
        """Initialize animation manager"""
        self.animation_cache: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def animate_line_chart(
        self,
        data: Dict[str, List],
        config: AnimationConfig = None
    ) -> Dict[str, Any]:
        """
        Create animated line chart with progressive line drawing.
        
        Args:
            data: Dictionary with 'x' and 'y' keys containing chart data
            config: Animation configuration
            
        Returns:
            Dictionary with figure and animation frames for Plotly
            
        Example:
            >>> data = {'x': [1, 2, 3], 'y': [10, 20, 15]}
            >>> result = manager.animate_line_chart(data)
        """
        if config is None:
            config = AnimationConfig(animation_type=AnimationType.LINE_DRAW)
        
        try:
            x_data = data.get('x', [])
            y_data = data.get('y', [])
            
            if not x_data or not y_data:
                self.logger.warning("Empty data provided for line animation")
                return {'frames': [], 'layout': {}}
            
            frames = []
            step = max(1, len(x_data) // config.frame_count)
            
            # Generate progressive frames
            for i in range(0, len(x_data), step):
                frame_data = {
                    'x': x_data[:i+step],
                    'y': y_data[:i+step],
                    'name': 'Line Animation'
                }
                frames.append(frame_data)
            
            layout = {
                'title': 'Line Chart Animation',
                'xaxis': {'title': 'X Axis'},
                'yaxis': {'title': 'Y Axis'},
                'hovermode': 'x unified',
                'transition': {
                    'duration': config.duration,
                    'easing': config.transition_type.value
                }
            }
            
            self.logger.info(f"Generated {len(frames)} animation frames")
            
            return {
                'frames': frames,
                'layout': layout,
                'duration': config.duration,
                'delay': config.delay
            }
        
        except Exception as e:
            self.logger.error(f"Error in line animation: {str(e)}")
            return {'frames': [], 'layout': {}}
    
    def animate_bar_race(
        self,
        data: List[Dict],
        x_col: str,
        y_col: str,
        time_col: str = None,
        config: AnimationConfig = None
    ) -> Dict[str, Any]:
        """
        Create animated bar racing chart.
        
        Args:
            data: List of dictionaries with chart data
            x_col: Column name for x-axis (categories)
            y_col: Column name for y-axis (values)
            time_col: Column name for time progression (optional)
            config: Animation configuration
            
        Returns:
            Dictionary with figure and animation frames
            
        Example:
            >>> data = [
            ...     {'category': 'A', 'value': 10, 'time': 0},
            ...     {'category': 'A', 'value': 20, 'time': 1}
            ... ]
            >>> result = manager.animate_bar_race(
            ...     data, 'category', 'value', 'time'
            ... )
        """
        if config is None:
            config = AnimationConfig(animation_type=AnimationType.BAR_RACE)
        
        try:
            if not data:
                self.logger.warning("Empty data for bar race animation")
                return {'frames': [], 'layout': {}}
            
            # Group by time if available
            if time_col and time_col in data[0]:
                grouped = self._group_by_time(data, time_col)
            else:
                grouped = [data]
            
            frames = []
            for group in grouped:
                # Sort by value for racing effect
                sorted_group = sorted(group, key=lambda x: x[y_col], reverse=True)
                
                frame = {
                    'x': [item[y_col] for item in sorted_group],
                    'y': [item[x_col] for item in sorted_group],
                    'type': 'bar',
                    'orientation': 'h'
                }
                frames.append(frame)
            
            layout = {
                'title': 'Bar Race Animation',
                'xaxis': {'title': y_col},
                'yaxis': {'title': x_col},
                'barmode': 'group',
                'transition': {
                    'duration': config.duration,
                    'easing': config.transition_type.value
                }
            }
            
            self.logger.info(f"Generated bar race with {len(frames)} frames")
            
            return {
                'frames': frames,
                'layout': layout,
                'duration': config.duration,
                'delay': config.delay
            }
        
        except Exception as e:
            self.logger.error(f"Error in bar race animation: {str(e)}")
            return {'frames': [], 'layout': {}}
    
    def animate_scatter(
        self,
        data: Dict[str, List],
        config: AnimationConfig = None
    ) -> Dict[str, Any]:
        """
        Create animated scatter plot with bubble/zoom effects.
        
        Args:
            data: Dictionary with 'x', 'y', and optional 'size' keys
            config: Animation configuration
            
        Returns:
            Dictionary with animation frames and layout
        """
        if config is None:
            config = AnimationConfig(animation_type=AnimationType.BUBBLE)
        
        try:
            x_data = data.get('x', [])
            y_data = data.get('y', [])
            size_data = data.get('size', [1] * len(x_data))
            
            frames = []
            step = max(1, len(x_data) // config.frame_count)
            
            for i in range(0, len(x_data), step):
                # Add zoom effect to marker size
                zoom_factor = (i + 1) / len(x_data) * 1.5
                
                frame = {
                    'x': x_data[:i+step],
                    'y': y_data[:i+step],
                    'mode': 'markers',
                    'marker': {
                        'size': [s * zoom_factor for s in size_data[:i+step]],
                        'opacity': 0.6,
                        'color': list(range(i+step)),
                        'colorscale': 'Viridis',
                        'showscale': True
                    }
                }
                frames.append(frame)
            
            layout = {
                'title': 'Scatter Animation',
                'xaxis': {'title': 'X Axis'},
                'yaxis': {'title': 'Y Axis'},
                'hovermode': 'closest',
                'transition': {
                    'duration': config.duration,
                    'easing': config.transition_type.value
                }
            }
            
            return {
                'frames': frames,
                'layout': layout,
                'duration': config.duration,
                'delay': config.delay
            }
        
        except Exception as e:
            self.logger.error(f"Error in scatter animation: {str(e)}")
            return {'frames': [], 'layout': {}}
    
    def add_smooth_transition(
        self,
        figure: Dict,
        duration: int = 500,
        easing: str = "cubic-in-out"
    ) -> Dict:
        """
        Add smooth transition effects to existing figure.
        
        Args:
            figure: Plotly figure dictionary
            duration: Transition duration in milliseconds
            easing: Easing function (linear, quad, cubic, elastic, bounce)
            
        Returns:
            Figure with transition applied
        """
        try:
            if 'layout' not in figure:
                figure['layout'] = {}
            
            figure['layout']['transition'] = {
                'duration': duration,
                'easing': easing
            }
            
            self.logger.info(f"Added smooth transition ({duration}ms, {easing})")
            return figure
        
        except Exception as e:
            self.logger.error(f"Error adding transition: {str(e)}")
            return figure
    
    def create_time_series_animation(
        self,
        time_steps: List[datetime],
        values: List[List[float]],
        labels: List[str] = None,
        config: AnimationConfig = None
    ) -> Dict[str, Any]:
        """
        Create animated time series with progressive data reveal.
        
        Args:
            time_steps: List of datetime objects
            values: List of value lists for each time step
            labels: Optional labels for series
            config: Animation configuration
            
        Returns:
            Dictionary with animation frames and layout
            
        Example:
            >>> times = [datetime(2025, 1, i) for i in range(1, 11)]
            >>> vals = [[i*10, i*15] for i in range(1, 11)]
            >>> result = manager.create_time_series_animation(times, vals)
        """
        if config is None:
            config = AnimationConfig()
        
        try:
            if not time_steps or not values:
                self.logger.warning("Empty time series data")
                return {'frames': [], 'layout': {}}
            
            frames = []
            step = max(1, len(time_steps) // config.frame_count)
            
            for i in range(step, len(time_steps) + 1, step):
                frame_times = time_steps[:i]
                frame_values = values[:i]
                
                frame = {
                    'x': [str(t) for t in frame_times],
                    'y': frame_values,
                    'mode': 'lines+markers'
                }
                frames.append(frame)
            
            layout = {
                'title': 'Time Series Animation',
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': 'Values'},
                'hovermode': 'x unified',
                'transition': {
                    'duration': config.duration,
                    'easing': config.transition_type.value
                }
            }
            
            return {
                'frames': frames,
                'layout': layout,
                'duration': config.duration,
                'delay': config.delay
            }
        
        except Exception as e:
            self.logger.error(f"Error in time series animation: {str(e)}")
            return {'frames': [], 'layout': {}}
    
    def _group_by_time(self, data: List[Dict], time_col: str) -> List[List[Dict]]:
        """
        Group data by time column.
        
        Args:
            data: List of dictionaries
            time_col: Time column name
            
        Returns:
            List of grouped data lists
        """
        try:
            grouped = {}
            for item in data:
                time_val = item.get(time_col)
                if time_val not in grouped:
                    grouped[time_val] = []
                grouped[time_val].append(item)
            
            return list(grouped.values())
        
        except Exception as e:
            self.logger.error(f"Error grouping data: {str(e)}")
            return [data]
    
    def get_animation_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about animation cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'total_cached': len(self.animation_cache),
            'cache_size_mb': sum(
                len(json.dumps(v)) / 1024 / 1024 
                for v in self.animation_cache.values()
            ),
            'cache_keys': list(self.animation_cache.keys())
        }
    
    def clear_cache(self) -> None:
        """Clear animation cache"""
        self.animation_cache.clear()
        self.logger.info("Animation cache cleared")


# Export public API
__all__ = [
    'PlotlyAnimationManager',
    'AnimationConfig',
    'AnimationType',
    'TransitionType'
]
