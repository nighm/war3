"""
JsonMapRepository的集成测试
"""
import pytest
import tempfile
import os
import json
from pathlib import Path
from src.infrastructure.repositories.json_map_repository import JsonMapRepository
from src.domain.entities.map_project import MapProject
from src.domain.value_objects.map_config import MapConfig


class TestJsonMapRepository:
    """JsonMapRepository集成测试类"""
    
    @pytest.fixture
    def temp_repo(self):
        """创建临时仓库"""
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_file = Path(temp_dir) / "projects.json"
            repo = JsonMapRepository(str(projects_file))
            yield repo
    
    @pytest.fixture
    def sample_project(self):
        """示例项目"""
        return MapProject(
            id="test_project_001",
            name="测试地图项目",
            project_type="RPG",
            paths={
                "root": "/test/path",
                "maps": "/test/path/maps",
                "custom": "/test/path/custom"
            },
            config=MapConfig(
                map_size="128x128",
                tileset="Lordaeron Summer",
                max_players=8
            ),
            resources={
                "models": 10,
                "textures": 25,
                "sounds": 15
            },
            status="active"
        )
    
    def test_save_and_find_project(self, temp_repo, sample_project):
        """测试保存和查找项目"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 查找项目
        found_project = temp_repo.find_by_id(sample_project.id)
        assert found_project is not None
        assert found_project.id == sample_project.id
        assert found_project.name == sample_project.name
        assert found_project.project_type == sample_project.project_type
    
    def test_find_all_projects(self, temp_repo, sample_project):
        """测试查找所有项目"""
        # 保存多个项目
        project2 = MapProject(
            id="test_project_002",
            name="测试地图项目2",
            project_type="TD",
            paths={"root": "/test/path2"},
            config=MapConfig(map_size="256x256", tileset="Lordaeron Summer"),
            resources={},
            status="active"
        )
        
        temp_repo.save(sample_project)
        temp_repo.save(project2)
        
        # 查找所有项目
        all_projects = temp_repo.find_all()
        assert len(all_projects) == 2
        
        project_ids = [p.id for p in all_projects]
        assert "test_project_001" in project_ids
        assert "test_project_002" in project_ids
    
    def test_update_existing_project(self, temp_repo, sample_project):
        """测试更新现有项目"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 更新项目
        sample_project.update_info(name="更新后的项目名称")
        temp_repo.save(sample_project)
        
        # 验证更新
        updated_project = temp_repo.find_by_id(sample_project.id)
        assert updated_project.name == "更新后的项目名称"
    
    def test_delete_project(self, temp_repo, sample_project):
        """测试删除项目"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 验证项目存在
        assert temp_repo.exists(sample_project.id)
        
        # 删除项目
        temp_repo.delete(sample_project.id)
        
        # 验证项目被删除
        assert not temp_repo.exists(sample_project.id)
        assert temp_repo.find_by_id(sample_project.id) is None
    
    def test_search_projects(self, temp_repo, sample_project):
        """测试搜索项目"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 搜索项目
        search_results = temp_repo.search("测试")
        assert len(search_results) == 1
        assert search_results[0].id == sample_project.id
        
        # 搜索不存在的项目
        no_results = temp_repo.search("不存在")
        assert len(no_results) == 0
    
    def test_count_projects(self, temp_repo, sample_project):
        """测试项目计数"""
        # 初始计数
        assert temp_repo.count() == 0
        
        # 保存项目
        temp_repo.save(sample_project)
        assert temp_repo.count() == 1
        
        # 保存另一个项目
        project2 = MapProject(
            id="test_project_002",
            name="测试地图项目2",
            project_type="TD",
            paths={"root": "/test/path2"},
            config=MapConfig(map_size="256x256", tileset="Lordaeron Summer"),
            resources={},
            status="active"
        )
        temp_repo.save(project2)
        assert temp_repo.count() == 2
    
    def test_backup_and_restore(self, temp_repo, sample_project):
        """测试备份和恢复"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 创建备份
        backup_file = temp_repo.backup_projects()
        assert Path(backup_file).exists()
        
        # 删除所有项目
        temp_repo.delete(sample_project.id)
        assert temp_repo.count() == 0
        
        # 从备份恢复
        temp_repo.restore_projects(backup_file)
        assert temp_repo.count() == 1
        
        # 验证恢复的项目
        restored_project = temp_repo.find_by_id(sample_project.id)
        assert restored_project is not None
        assert restored_project.name == sample_project.name
    
    def test_persistence_across_instances(self, temp_repo, sample_project):
        """测试跨实例持久化"""
        # 保存项目
        temp_repo.save(sample_project)
        
        # 创建新的仓库实例（使用相同的文件）
        new_repo = JsonMapRepository(temp_repo.projects_file)
        
        # 验证项目仍然存在
        assert new_repo.exists(sample_project.id)
        found_project = new_repo.find_by_id(sample_project.id)
        assert found_project.name == sample_project.name
