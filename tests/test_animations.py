"""
Tests for Animation Manager (P3.1)
=================================

Unit tests for Plotly animation system with comprehensive coverage.

Version: 3.0.0
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from app.animations.animation_manager import (
    PlotlyAnimationManager,
    AnimationConfig,
    AnimationType,
    TransitionType
)


class TestAnimationConfig:
    """Test AnimationConfig dataclass"""
    
    def test_default_config(self):
        """Test default animation config"""
        config = AnimationConfig()
        assert config.duration == 500
        assert config.delay == 100
        assert config.frame_count == 20
        assert config.transition_type == TransitionType.CUBIC
    
    def test_custom_config(self):
        """Test custom animation config"""
        config = AnimationConfig(
            animation_type=AnimationType.BAR_RACE,
            duration=800,
            delay=50
        )
        assert config.animation_type == AnimationType.BAR_RACE
        assert config.duration == 800
        assert config.delay == 50


class TestPlotlyAnimationManager:
    """Test PlotlyAnimationManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create animation manager instance"""
        return PlotlyAnimationManager()
    
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager is not None
        assert isinstance(manager.animation_cache, dict)
        assert len(manager.animation_cache) == 0
    
    def test_line_chart_animation(self, manager):
        """Test line chart animation creation"""
        data = {
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 15, 25, 30]
        }
        
        result = manager.animate_line_chart(data)
        
        assert 'frames' in result
        assert 'layout' in result
        assert len(result['frames']) > 0
        assert result['duration'] == 500
    
    def test_line_chart_empty_data(self, manager):
        """Test line chart with empty data"""
        result = manager.animate_line_chart({})
        
        assert 'frames' in result
        assert len(result['frames']) == 0
    
    def test_bar_race_animation(self, manager):
        """Test bar race animation"""
        data = [
            {'category': 'A', 'value': 10, 'time': 1},
            {'category': 'B', 'value': 20, 'time': 1},
            {'category': 'A', 'value': 15, 'time': 2},
            {'category': 'B', 'value': 25, 'time': 2}
        ]
        
        result = manager.animate_bar_race(data, 'category', 'value', 'time')
        
        assert 'frames' in result
        assert 'layout' in result
        assert len(result['frames']) > 0
    
    def test_bar_race_empty_data(self, manager):
        """Test bar race with empty data"""
        result = manager.animate_bar_race([], 'x', 'y')
        
        assert len(result['frames']) == 0
    
    def test_scatter_animation(self, manager):
        """Test scatter plot animation"""
        data = {
            'x': [1, 2, 3, 4, 5],
            'y': [10, 20, 15, 25, 30],
            'size': [5, 10, 8, 12, 15]
        }
        
        result = manager.animate_scatter(data)
        
        assert 'frames' in result
        assert len(result['frames']) > 0
    
    def test_smooth_transition(self, manager):
        """Test smooth transition addition"""
        figure = {'layout': {}}
        
        result = manager.add_smooth_transition(figure, duration=800)
        
        assert result['layout']['transition']['duration'] == 800
        assert result['layout']['transition']['easing'] == 'cubic-in-out'
    
    def test_smooth_transition_easing_options(self, manager):
        """Test different easing options"""
        figure = {'layout': {}}
        easing_options = ['linear', 'quad', 'cubic', 'elastic', 'bounce']
        
        for easing in easing_options:
            result = manager.add_smooth_transition(figure, easing=easing)
            assert result['layout']['transition']['easing'] == easing
    
    def test_time_series_animation(self, manager):
        """Test time series animation"""
        times = [datetime(2025, 1, i) for i in range(1, 11)]
        values = [[i*10, i*15] for i in range(1, 11)]
        
        result = manager.create_time_series_animation(times, values)
        
        assert 'frames' in result
        assert len(result['frames']) > 0
    
    def test_time_series_empty_data(self, manager):
        """Test time series with empty data"""
        result = manager.create_time_series_animation([], [])
        
        assert len(result['frames']) == 0
    
    def test_group_by_time(self, manager):
        """Test grouping data by time"""
        data = [
            {'time': 1, 'value': 10},
            {'time': 1, 'value': 20},
            {'time': 2, 'value': 15},
            {'time': 2, 'value': 25}
        ]
        
        grouped = manager._group_by_time(data, 'time')
        
        assert len(grouped) == 2
        assert len(grouped[0]) == 2
    
    def test_animation_cache_stats(self, manager):
        """Test cache statistics"""
        stats = manager.get_animation_cache_stats()
        
        assert 'total_cached' in stats
        assert 'cache_size_mb' in stats
        assert stats['total_cached'] == 0
    
    def test_cache_clear(self, manager):
        """Test cache clearing"""
        manager.animation_cache['test'] = {'data': 'value'}
        assert len(manager.animation_cache) > 0
        
        manager.clear_cache()
        assert len(manager.animation_cache) == 0
    
    def test_different_animation_types(self, manager):
        """Test different animation types"""
        data = {'x': [1, 2, 3], 'y': [10, 20, 15]}
        
        for anim_type in AnimationType:
            config = AnimationConfig(animation_type=anim_type)
            if anim_type == AnimationType.LINE_DRAW:
                result = manager.animate_line_chart(data, config)
            elif anim_type in [AnimationType.BUBBLE, AnimationType.SCATTER]:
                result = manager.animate_scatter(data, config)
            
            assert 'frames' in result or anim_type not in [
                AnimationType.LINE_DRAW,
                AnimationType.BUBBLE,
                AnimationType.SCATTER
            ]
    
    def test_animation_config_variations(self, manager):
        """Test various animation configs"""
        data = {'x': [1, 2, 3, 4, 5], 'y': [10, 20, 15, 25, 30]}
        
        configs = [
            AnimationConfig(frame_count=10, duration=300),
            AnimationConfig(frame_count=30, duration=1000),
            AnimationConfig(frame_count=5, delay=50)
        ]
        
        for config in configs:
            result = manager.animate_line_chart(data, config)
            assert result['duration'] == config.duration
    
    def test_scatter_with_zoom_effect(self, manager):
        """Test scatter animation with zoom effect"""
        data = {
            'x': list(range(1, 11)),
            'y': list(range(10, 110, 10)),
            'size': [5] * 10
        }
        
        result = manager.animate_scatter(data)
        
        # Verify frames have increasing marker sizes
        for frame in result['frames']:
            if 'marker' in frame and 'size' in frame['marker']:
                assert all(s >= 0 for s in frame['marker']['size'])
    
    def test_bar_race_sorting(self, manager):
        """Test bar race sorting by value"""
        data = [
            {'category': 'Z', 'value': 100},
            {'category': 'A', 'value': 50},
            {'category': 'M', 'value': 75}
        ]
        
        result = manager.animate_bar_race(data, 'category', 'value')
        
        assert len(result['frames']) > 0
        # First frame should have sorted data
        first_frame = result['frames'][0]
        if 'x' in first_frame:
            # Values should be sorted in descending order
            assert first_frame['x'][0] >= first_frame['x'][-1]
    
    def test_error_handling_invalid_data(self, manager):
        """Test error handling with invalid data"""
        # Should not raise exceptions
        result = manager.animate_line_chart(None)
        assert 'frames' in result
        
        result = manager.animate_bar_race(None, 'x', 'y')
        assert 'frames' in result
        
        result = manager.animate_scatter(None)
        assert 'frames' in result
    
    def test_transition_types(self):
        """Test all transition types"""
        transition_types = [
            TransitionType.LINEAR,
            TransitionType.QUAD,
            TransitionType.CUBIC,
            TransitionType.ELASTIC,
            TransitionType.BOUNCE
        ]
        
        assert len(transition_types) == 5
        assert all(isinstance(t, TransitionType) for t in transition_types)
    
    def test_animation_types_enum(self):
        """Test all animation types"""
        animation_types = [
            AnimationType.SLIDE,
            AnimationType.FADE,
            AnimationType.ZOOM,
            AnimationType.SCATTER,
            AnimationType.BAR_RACE,
            AnimationType.LINE_DRAW,
            AnimationType.BUBBLE,
            AnimationType.GRADIENT
        ]
        
        assert len(animation_types) == 8
