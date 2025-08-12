"""
MapRepository接口的单元测试
"""
import pytest
from unittest.mock import Mock, patch
from uuid import UUID
from pathlib import Path
from src.domain.repositories.map_repository import MapRepository
from src.domain.entities.map_project import MapProject


class TestMapRepository:
    """MapRepository接口测试类"""
    
    def test_map_repository_is_abstract(self):
        """测试MapRepository是抽象类"""
        with pytest.raises(TypeError):
            MapRepository()
    
    def test_map_repository_has_required_methods(self):
        """测试MapRepository有必需的方法"""
        # 检查抽象方法是否存在
        assert hasattr(MapRepository, 'save')
        assert hasattr(MapRepository, 'find_by_id')
        assert hasattr(MapRepository, 'find_by_name')
        assert hasattr(MapRepository, 'find_by_path')
        assert hasattr(MapRepository, 'find_all')
        assert hasattr(MapRepository, 'find_by_type')
        assert hasattr(MapRepository, 'find_active')
        assert hasattr(MapRepository, 'find_archived')
        assert hasattr(MapRepository, 'delete')
        assert hasattr(MapRepository, 'exists')
        assert hasattr(MapRepository, 'count')
        assert hasattr(MapRepository, 'search')
        assert hasattr(MapRepository, 'get_project_stats')
    
    def test_map_repository_method_signatures(self):
        """测试MapRepository方法签名"""
        # 使用Mock来检查方法签名
        mock_repo = Mock(spec=MapRepository)
        
        # 测试save方法
        project = MapProject(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="测试项目",
            project_type="rpg",
            project_path=Path("/test"),
            config={
                "map_name": "测试地图",
                "map_description": "这是一个测试地图",
                "map_author": "测试作者"
            },
            resources={}
        )
        
        # 这些调用应该不会抛出异常
        mock_repo.save(project)
        mock_repo.find_by_id("test_id")
        mock_repo.find_by_name("测试项目")
        mock_repo.find_all()
        mock_repo.delete("test_id")
        mock_repo.exists("test_id")
        mock_repo.count()
        mock_repo.search("测试")
        mock_repo.get_project_stats()
        
        # 验证方法被调用
        assert mock_repo.save.called
        assert mock_repo.find_by_id.called
        assert mock_repo.find_by_name.called
        assert mock_repo.find_all.called
        assert mock_repo.delete.called
        assert mock_repo.exists.called
        assert mock_repo.count.called
        assert mock_repo.search.called
        assert mock_repo.get_project_stats.called
