"""
pytest配置文件
设置测试环境和共享fixture
"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试数据目录
@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return project_root / "tests" / "test_data"

@pytest.fixture(scope="session")
def temp_dir():
    """临时目录"""
    return project_root / "tests" / "temp"

@pytest.fixture(scope="function")
def sample_project_data():
    """示例项目数据"""
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "name": "测试地图项目",
        "project_type": "RPG",
        "paths": {
            "root": "/test/path",
            "maps": "/test/path/maps",
            "custom": "/test/path/custom"
        },
        "config": {
            "map_name": "测试地图",
            "map_description": "这是一个测试地图",
            "map_author": "测试作者",
            "map_size": "large",
            "terrain_type": "forest",
            "max_players": 8
        },
        "resources": {
            "models": ["/path/to/model1.mdx", "/path/to/model2.mdx"],
            "textures": ["/path/to/texture1.blp", "/path/to/texture2.blp"],
            "sounds": ["/path/to/sound1.wav", "/path/to/sound2.wav"]
        },
        "status": "active"
    }

@pytest.fixture(scope="function")
def mock_file_system(tmp_path):
    """模拟文件系统"""
    # 创建测试目录结构
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    (project_dir / "maps").mkdir()
    (project_dir / "custom").mkdir()
    (project_dir / "custom" / "models").mkdir()
    (project_dir / "custom" / "textures").mkdir()
    
    # 创建测试文件
    (project_dir / "maps" / "test.map").write_text("test map content")
    (project_dir / "custom" / "models" / "test.mdx").write_text("test model")
    (project_dir / "custom" / "textures" / "test.blp").write_text("test texture")
    
    return project_dir
