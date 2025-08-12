"""
ProjectService的集成测试
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock
from src.application.services.project_service import ProjectService
from src.infrastructure.repositories.json_map_repository import JsonMapRepository
from src.domain.services.map_analysis_service import DefaultMapAnalysisService
from src.domain.entities.map_project import MapProject
from src.domain.value_objects.map_config import MapConfig


class TestProjectService:
    """ProjectService集成测试类"""
    
    @pytest.fixture
    def temp_repo(self):
        """创建临时仓库"""
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_file = Path(temp_dir) / "projects.json"
            repo = JsonMapRepository(str(projects_file))
            yield repo
    
    @pytest.fixture
    def analysis_service(self):
        """创建分析服务"""
        return DefaultMapAnalysisService()
    
    @pytest.fixture
    def project_service(self, temp_repo, analysis_service):
        """创建项目服务"""
        return ProjectService(temp_repo, analysis_service)
    
    @pytest.fixture
    def sample_project_data(self):
        """示例项目数据"""
        return {
            "name": "测试地图项目",
            "project_type": "RPG",
            "paths": {
                "root": "/test/path",
                "maps": "/test/path/maps",
                "custom": "/test/path/custom"
            },
            "config": {
                "map_size": "128x128",
                "tileset": "Lordaeron Summer",
                "max_players": 8
            }
        }
    
    def test_create_project(self, project_service, sample_project_data, mock_file_system):
        """测试创建项目"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        assert project is not None
        assert project.name == sample_project_data["name"]
        assert project.project_type == sample_project_data["project_type"]
        assert project.status == "active"
        
        # 验证项目被保存到仓库
        saved_project = project_service.map_repository.find_by_id(project.id)
        assert saved_project is not None
        assert saved_project.name == project.name
    
    def test_open_project(self, project_service, sample_project_data, mock_file_system):
        """测试打开项目"""
        # 先创建一个项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 打开项目
        opened_project = project_service.open_project(project.id)
        assert opened_project is not None
        assert opened_project.id == project.id
        assert opened_project.name == project.name
    
    def test_save_project(self, project_service, sample_project_data, mock_file_system):
        """测试保存项目"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 修改项目
        project.update_info(name="修改后的项目名称")
        
        # 保存项目
        project_service.save_project(project)
        
        # 验证保存
        saved_project = project_service.map_repository.find_by_id(project.id)
        assert saved_project.name == "修改后的项目名称"
    
    def test_delete_project(self, project_service, sample_project_data, mock_file_system):
        """测试删除项目"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 验证项目存在
        assert project_service.map_repository.exists(project.id)
        
        # 删除项目
        project_service.delete_project(project.id)
        
        # 验证项目被删除
        assert not project_service.map_repository.exists(project.id)
    
    def test_analyze_project(self, project_service, sample_project_data, mock_file_system):
        """测试分析项目"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 分析项目
        analysis_result = project_service.analyze_project(project.id)
        assert analysis_result is not None
        assert "structure" in analysis_result
        assert "resources" in analysis_result
        assert "performance" in analysis_result
    
    def test_list_projects(self, project_service, sample_project_data, mock_file_system):
        """测试列出项目"""
        # 创建多个项目
        project1 = project_service.create_project(
            name="项目1",
            project_type="RPG",
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        project2 = project_service.create_project(
            name="项目2",
            project_type="TD",
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 列出所有项目
        projects = project_service.list_projects()
        assert len(projects) == 2
        
        project_names = [p.name for p in projects]
        assert "项目1" in project_names
        assert "项目2" in project_names
    
    def test_search_projects(self, project_service, sample_project_data, mock_file_system):
        """测试搜索项目"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 搜索项目
        search_results = project_service.search_projects("测试")
        assert len(search_results) == 1
        assert search_results[0].id == project.id
        
        # 搜索不存在的项目
        no_results = project_service.search_projects("不存在")
        assert len(no_results) == 0
    
    def test_batch_analyze_projects(self, project_service, sample_project_data, mock_file_system):
        """测试批量分析项目"""
        # 创建多个项目
        project1 = project_service.create_project(
            name="项目1",
            project_type="RPG",
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        project2 = project_service.create_project(
            name="项目2",
            project_type="TD",
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 批量分析
        batch_result = project_service.batch_analyze_projects()
        assert batch_result is not None
        assert batch_result.total_projects == 2
        assert batch_result.successful_operations == 2
        assert batch_result.failed_operations == 0
    
    def test_generate_report(self, project_service, sample_project_data, mock_file_system):
        """测试生成报告"""
        # 创建项目
        project = project_service.create_project(
            name=sample_project_data["name"],
            project_type=sample_project_data["project_type"],
            project_path=str(mock_file_system),
            config_data=sample_project_data["config"]
        )
        
        # 生成报告
        report = project_service.generate_report(project.id)
        assert report is not None
        assert "project_info" in report
        assert "analysis_results" in report
        assert "recommendations" in report
