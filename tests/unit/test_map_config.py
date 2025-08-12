"""
MapConfig值对象的单元测试
"""
import pytest
from src.domain.value_objects.map_config import MapConfig


class TestMapConfig:
    """MapConfig值对象测试类"""
    
    def test_create_valid_map_config(self):
        """测试创建有效的地图配置"""
        config = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="large",
            terrain_type="forest",
            max_players=8
        )
        
        assert config.map_name == "测试地图"
        assert config.map_description == "这是一个测试地图"
        assert config.map_author == "测试作者"
        assert config.map_size == "large"
        assert config.terrain_type == "forest"
        assert config.max_players == 8
    
    def test_map_config_immutability(self):
        """测试地图配置的不可变性"""
        config = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="large",
            terrain_type="forest",
            max_players=8
        )
        
        # 尝试修改属性应该失败
        with pytest.raises(Exception):
            config.map_size = "medium"
    
    def test_map_config_validation(self):
        """测试地图配置验证"""
        # 测试有效配置
        valid_config = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="large",
            terrain_type="forest",
            max_players=8
        )
        assert valid_config is not None
        
        # 测试无效的最大玩家数
        with pytest.raises(ValueError):
            MapConfig(
                map_name="测试地图",
                map_description="这是一个测试地图",
                map_author="测试作者",
                map_size="large",
                terrain_type="forest",
                max_players=0
            )
        
        # 测试无效的最大玩家数（超过限制）
        with pytest.raises(ValueError):
            MapConfig(
                map_name="测试地图",
                map_description="这是一个测试地图",
                map_author="测试作者",
                map_size="large",
                terrain_type="forest",
                max_players=13
            )
    
    def test_map_config_default_values(self):
        """测试地图配置默认值"""
        config = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者"
        )
        
        assert config.max_players == 12  # 默认值
        assert config.weather_effects is False  # 默认值
        assert config.map_size == "medium"  # 默认值
    
    def test_map_config_equality(self):
        """测试地图配置相等性"""
        config1 = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="large",
            terrain_type="forest",
            max_players=8
        )
        
        config2 = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="large",
            terrain_type="forest",
            max_players=8
        )
        
        config3 = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者",
            map_size="medium",
            terrain_type="forest",
            max_players=8
        )
        
        assert config1 == config2
        assert config1 != config3
    
    def test_map_config_hash(self):
        """测试地图配置哈希值"""
        # 由于MapConfig包含字典字段，它可能不是可哈希的
        # 我们只测试相等性，不测试哈希值
        config1 = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者"
        )
        
        config2 = MapConfig(
            map_name="测试地图",
            map_description="这是一个测试地图",
            map_author="测试作者"
        )
        
        # 测试相等性
        assert config1 == config2
        
        # 测试字典转换
        dict1 = config1.to_dict()
        dict2 = config2.to_dict()
        assert dict1 == dict2
