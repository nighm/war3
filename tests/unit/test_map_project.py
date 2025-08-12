"""
MapProject实体的单元测试
"""
import pytest
from uuid import UUID
from pathlib import Path
from src.domain.entities.map_project import MapProject


class TestMapProject:
    """MapProject实体测试类"""
    
    def test_create_map_project(self, sample_project_data):
        """测试创建地图项目"""
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=Path(sample_project_data["paths"]["root"]),
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        assert str(project.id) == sample_project_data["id"]
        assert project.name == sample_project_data["name"]
        assert project.project_type == sample_project_data["project_type"]
        assert project.is_active is True
    
    def test_update_project_info(self, sample_project_data):
        """测试更新项目信息"""
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=Path(sample_project_data["paths"]["root"]),
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        # 更新项目名称
        project.update_project_info(name="新项目名称")
        assert project.name == "新项目名称"
        
        # 更新项目类型
        project.update_project_info(project_type="td")
        assert project.project_type == "td"
    
    def test_manage_resources(self, sample_project_data):
        """测试资源管理"""
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=Path(sample_project_data["paths"]["root"]),
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        # 添加资源
        project.add_resource("models", "/path/to/model.mdx")
        assert len(project.resources["models"]) == 3
        
        # 移除资源
        project.remove_resource("textures", "/path/to/texture1.blp")
        assert len(project.resources["textures"]) == 1
    
    def test_archive_and_activate(self, sample_project_data):
        """测试归档和激活"""
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=Path(sample_project_data["paths"]["root"]),
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        # 归档项目
        project.archive_project()
        assert project.is_archived is True
        assert project.is_active is False
        
        # 激活项目
        project.activate_project()
        assert project.is_archived is False
        assert project.is_active is True
    
    def test_validation(self, sample_project_data, tmp_path):
        """测试项目验证"""
        # 创建真实的项目路径
        real_project_path = tmp_path / "test_project"
        real_project_path.mkdir()
        
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type="rpg",  # 使用有效的项目类型
            project_path=real_project_path,
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        # 验证有效项目
        validation_errors = project.validate_project()
        assert len(validation_errors) == 0
        
        # 测试无效项目（缺少必要字段）
        invalid_project = MapProject(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="",
            project_type="invalid_type",
            project_path=Path("/nonexistent/path"),
            config={},
            resources={}
        )
        
        validation_errors = invalid_project.validate_project()
        assert len(validation_errors) > 0
    
    def test_to_dict_and_from_dict(self, sample_project_data):
        """测试字典转换"""
        project = MapProject(
            id=UUID(sample_project_data["id"]),
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=Path(sample_project_data["paths"]["root"]),
            config=sample_project_data["config"],
            resources=sample_project_data["resources"]
        )
        
        # 转换为字典
        project_dict = project.to_dict()
        assert isinstance(project_dict, dict)
        assert project_dict["id"] == str(project.id)
        assert project_dict["name"] == project.name
        
        # 从字典创建
        new_project = MapProject.from_dict(project_dict)
        assert str(new_project.id) == str(project.id)
        assert new_project.name == project.name
        assert new_project.project_type == project.project_type
