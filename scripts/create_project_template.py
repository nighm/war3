#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔兽争霸3地图开发项目模板生成器
自动创建标准的地图开发项目结构
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ProjectTemplateGenerator:
    """项目模板生成器"""
    
    def __init__(self):
        """初始化模板生成器"""
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.output_dir = Path.cwd()
        
        # 项目类型模板
        self.project_types = {
            "rpg": {
                "name": "RPG地图",
                "description": "角色扮演游戏地图",
                "features": ["任务系统", "等级系统", "装备系统", "技能系统"]
            },
            "td": {
                "name": "塔防地图",
                "description": "防御类游戏地图",
                "features": ["塔防系统", "波次系统", "经济系统", "升级系统"]
            },
            "moba": {
                "name": "MOBA地图",
                "description": "多人在线战术竞技地图",
                "features": ["英雄系统", "装备系统", "技能系统", "团队系统"]
            },
            "survival": {
                "name": "生存地图",
                "description": "生存挑战类游戏地图",
                "features": ["生存系统", "资源系统", "建造系统", "探索系统"]
            },
            "melee": {
                "name": "对战地图",
                "description": "传统即时战略对战地图",
                "features": ["资源系统", "建造系统", "兵种系统", "战术系统"]
            }
        }
    
    def create_project(self, project_name: str, project_type: str, 
                      author: str = "", description: str = "") -> bool:
        """
        创建新项目
        
        Args:
            project_name: 项目名称
            project_type: 项目类型
            author: 作者名称
            description: 项目描述
        
        Returns:
            是否创建成功
        """
        try:
            # 验证项目类型
            if project_type not in self.project_types:
                print(f"❌ 不支持的项目类型: {project_type}")
                print(f"支持的类型: {', '.join(self.project_types.keys())}")
                return False
            
            # 创建项目目录
            project_path = self.output_dir / project_name
            if project_path.exists():
                print(f"❌ 项目目录已存在: {project_path}")
                return False
            
            project_path.mkdir(parents=True)
            print(f"✅ 创建项目目录: {project_path}")
            
            # 创建项目结构
            self._create_project_structure(project_path, project_type)
            
            # 创建配置文件
            self._create_project_config(project_path, project_name, project_type, 
                                     author, description)
            
            # 创建文档
            self._create_project_docs(project_path, project_name, project_type)
            
            # 创建地图文件
            self._create_map_file(project_path, project_name, project_type)
            
            # 创建触发器模板
            self._create_trigger_templates(project_path, project_type)
            
            # 创建单位模板
            self._create_unit_templates(project_path, project_type)
            
            print(f"✅ 项目 '{project_name}' 创建成功！")
            print(f"📁 项目路径: {project_path}")
            print(f"📖 请查看 README.md 了解项目结构和使用方法")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建项目失败: {e}")
            return False
    
    def _create_project_structure(self, project_path: Path, project_type: str) -> None:
        """创建项目目录结构"""
        # 创建主要目录
        directories = [
            "docs",           # 文档目录
            "maps",           # 地图文件
            "triggers",       # 触发器代码
            "units",          # 单位数据
            "items",          # 物品数据
            "resources",      # 资源文件
            "scripts",        # 脚本工具
            "backups",        # 备份文件
            "logs",           # 日志文件
            "tests",          # 测试文件
            "exports"         # 导出文件
        ]
        
        for directory in directories:
            (project_path / directory).mkdir(exist_ok=True)
        
        # 创建子目录
        (project_path / "resources" / "models").mkdir(parents=True, exist_ok=True)
        (project_path / "resources" / "textures").mkdir(parents=True, exist_ok=True)
        (project_path / "resources" / "sounds").mkdir(parents=True, exist_ok=True)
        (project_path / "resources" / "music").mkdir(parents=True, exist_ok=True)
        
        (project_path / "docs" / "design").mkdir(parents=True, exist_ok=True)
        (project_path / "docs" / "api").mkdir(parents=True, exist_ok=True)
        
        print("✅ 创建项目目录结构完成")
    
    def _create_project_config(self, project_path: Path, project_name: str, 
                             project_type: str, author: str, description: str) -> None:
        """创建项目配置文件"""
        config_data = {
            "project_info": {
                "name": project_name,
                "type": project_type,
                "author": author or "Unknown",
                "description": description or self.project_types[project_type]["description"],
                "version": "1.0.0",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "last_modified": datetime.now().strftime("%Y-%m-%d")
            },
            "map_settings": {
                "map_size": "128x128",
                "tileset": "Lordaeron Summer",
                "players": 4,
                "max_players": 8,
                "map_name": project_name,
                "map_description": description
            },
            "development": {
                "auto_save": True,
                "backup_enabled": True,
                "version_control": True,
                "log_level": "INFO"
            },
            "editor_settings": {
                "default_editor": "world_editor",
                "jass_mode": False,
                "auto_backup_interval": 5
            }
        }
        
        # 保存YAML配置
        import yaml
        config_file = project_path / "project_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, 
                     allow_unicode=True, indent=2)
        
        print("✅ 创建项目配置文件完成")
    
    def _create_project_docs(self, project_path: Path, project_name: str, 
                            project_type: str) -> None:
        """创建项目文档"""
        # 创建README.md
        readme_content = f"""# {project_name}

## 项目概述

这是一个{self.project_types[project_type]['name']}，{self.project_types[project_type]['description']}。

## 项目结构

```
{project_name}/
├── docs/                    # 文档目录
│   ├── design/             # 设计文档
│   └── api/                # API文档
├── maps/                   # 地图文件
├── triggers/               # 触发器代码
├── units/                  # 单位数据
├── items/                  # 物品数据
├── resources/              # 资源文件
│   ├── models/            # 模型文件
│   ├── textures/          # 贴图文件
│   ├── sounds/            # 音效文件
│   └── music/             # 音乐文件
├── scripts/                # 脚本工具
├── backups/                # 备份文件
├── logs/                   # 日志文件
├── tests/                  # 测试文件
└── exports/                # 导出文件
```

## 开发指南

### 1. 环境准备
- 确保已安装魔兽争霸3
- 配置World Editor路径
- 可选：安装JNGP工具

### 2. 开发流程
1. 使用World Editor创建基础地图
2. 设计地形和装饰物
3. 创建自定义单位和物品
4. 编写触发器逻辑
5. 测试和调试
6. 优化和发布

### 3. 文件说明
- `maps/`: 存放地图文件(.w3x)
- `triggers/`: 存放JASS触发器代码
- `units/`: 存放单位数据文件
- `items/`: 存放物品数据文件
- `resources/`: 存放自定义资源文件

### 4. 版本控制
- 定期备份地图文件
- 使用Git管理项目文件
- 记录重要修改和更新

## 功能特性

{chr(10).join([f"- {feature}" for feature in self.project_types[project_type]['features']])}

## 开发工具

- **World Editor**: 官方地图编辑器
- **JNGP**: 增强的JASS编辑器（可选）
- **MPQ Editor**: 资源文件管理工具

## 发布说明

1. 测试地图功能完整性
2. 优化地图文件大小
3. 压缩和打包地图文件
4. 上传到地图平台

---

**注意**: 请确保使用正版魔兽争霸3进行开发。
"""
        
        readme_file = project_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # 创建设计文档模板
        design_doc_content = f"""# {project_name} 设计文档

## 1. 项目概述

### 1.1 项目名称
{project_name}

### 1.2 项目类型
{self.project_types[project_type]['name']}

### 1.3 项目描述
{self.project_types[project_type]['description']}

## 2. 游戏设计

### 2.1 核心玩法
[描述游戏的核心玩法机制]

### 2.2 胜利条件
[描述游戏的胜利条件]

### 2.3 失败条件
[描述游戏的失败条件]

## 3. 地图设计

### 3.1 地形布局
[描述地图的地形设计]

### 3.2 资源分布
[描述地图上的资源分布]

### 3.3 建筑布局
[描述地图上的建筑布局]

## 4. 单位设计

### 4.1 玩家单位
[描述玩家可控制的单位]

### 4.2 中立单位
[描述地图上的中立单位]

### 4.3 敌对单位
[描述敌对单位]

## 5. 物品设计

### 5.1 装备物品
[描述装备类物品]

### 5.2 消耗物品
[描述消耗类物品]

### 5.3 任务物品
[描述任务相关物品]

## 6. 触发器设计

### 6.1 初始化触发器
[描述游戏初始化逻辑]

### 6.2 游戏逻辑触发器
[描述主要游戏逻辑]

### 6.3 事件触发器
[描述各种事件处理]

## 7. 音效设计

### 7.1 背景音乐
[描述背景音乐设计]

### 7.2 音效
[描述各种音效]

## 8. 平衡性设计

### 8.1 数值平衡
[描述数值平衡设计]

### 8.2 机制平衡
[描述机制平衡设计]

## 9. 测试计划

### 9.1 功能测试
[描述功能测试计划]

### 9.2 平衡性测试
[描述平衡性测试计划]

### 9.3 用户体验测试
[描述用户体验测试计划]

## 10. 发布计划

### 10.1 开发阶段
[描述开发阶段计划]

### 10.2 测试阶段
[描述测试阶段计划]

### 10.3 发布阶段
[描述发布阶段计划]
"""
        
        design_doc_file = project_path / "docs" / "design" / "design_document.md"
        with open(design_doc_file, 'w', encoding='utf-8') as f:
            f.write(design_doc_content)
        
        print("✅ 创建项目文档完成")
    
    def _create_map_file(self, project_path: Path, project_name: str, 
                         project_type: str) -> None:
        """创建地图文件模板"""
        # 创建地图文件说明
        map_info_content = f"""# 地图文件说明

## 地图信息
- 地图名称: {project_name}
- 地图类型: {self.project_types[project_type]['name']}
- 地图大小: 128x128
- 玩家数量: 4-8人
- 地形类型: Lordaeron Summer

## 使用说明
1. 将地图文件(.w3x)放在此目录
2. 地图文件命名格式: {project_name}.w3x
3. 定期备份地图文件
4. 使用版本控制管理地图文件

## 开发建议
- 使用World Editor创建基础地图
- 保存多个版本的地图文件
- 定期测试地图功能
- 优化地图文件大小
"""
        
        map_info_file = project_path / "maps" / "README.md"
        with open(map_info_file, 'w', encoding='utf-8') as f:
            f.write(map_info_content)
        
        print("✅ 创建地图文件模板完成")
    
    def _create_trigger_templates(self, project_path: Path, project_type: str) -> None:
        """创建触发器模板"""
        # 基础触发器模板
        base_trigger_content = """// 基础触发器模板
// 项目类型: {project_type}
// 创建时间: {created_date}

// 游戏初始化触发器
function InitGame takes nothing returns nothing
    // 设置游戏参数
    call SetGameSpeed( MAP_SPEED_FAST )
    call SetMapFlag( MAP_FOG_HIDE_TERRAIN, false )
    call SetMapFlag( MAP_FOG_MASKED_PLAYER, false )
    
    // 初始化玩家数据
    call InitPlayerData()
    
    // 初始化游戏系统
    call InitGameSystems()
endfunction

// 初始化玩家数据
function InitPlayerData takes nothing returns nothing
    local integer i = 0
    loop
        exitwhen i >= 8
        if GetPlayerController(Player(i)) == MAP_CONTROL_USER then
            // 设置玩家初始资源
            call SetPlayerState(Player(i), PLAYER_STATE_RESOURCE_GOLD, 1000)
            call SetPlayerState(Player(i), PLAYER_STATE_RESOURCE_LUMBER, 500)
        endif
        set i = i + 1
    endloop
endfunction

// 初始化游戏系统
function InitGameSystems takes nothing returns nothing
    // 根据项目类型初始化不同系统
    {system_init_code}
endfunction

// 胜利条件检查
function CheckVictoryConditions takes nothing returns nothing
    // 实现胜利条件检查逻辑
endfunction

// 失败条件检查
function CheckDefeatConditions takes nothing returns nothing
    // 实现失败条件检查逻辑
endfunction
"""
        
        # 根据项目类型生成不同的系统初始化代码
        system_init_codes = {
            "rpg": """// RPG系统初始化
    call InitRPGSystems()""",
            "td": """// 塔防系统初始化
    call InitTowerDefenseSystems()""",
            "moba": """// MOBA系统初始化
    call InitMOBASystems()""",
            "survival": """// 生存系统初始化
    call InitSurvivalSystems()""",
            "melee": """// 对战系统初始化
    call InitMeleeSystems()"""
        }
        
        trigger_content = base_trigger_content.format(
            project_type=project_type,
            created_date=datetime.now().strftime("%Y-%m-%d"),
            system_init_code=system_init_codes.get(project_type, "// 基础系统初始化")
        )
        
        trigger_file = project_path / "triggers" / "base_triggers.j"
        with open(trigger_file, 'w', encoding='utf-8') as f:
            f.write(trigger_content)
        
        print("✅ 创建触发器模板完成")
    
    def _create_unit_templates(self, project_path: Path, project_type: str) -> None:
        """创建单位模板"""
        # 单位数据模板
        unit_template_content = f"""# 单位数据模板

## 项目类型: {project_type}

### 自定义单位列表

#### 1. 英雄单位
- 英雄名称: [英雄名称]
- 单位类型: 英雄
- 主要属性: [力量/敏捷/智力]
- 技能列表:
  - 技能1: [技能名称] - [技能描述]
  - 技能2: [技能名称] - [技能描述]
  - 技能3: [技能名称] - [技能描述]
  - 终极技能: [技能名称] - [技能描述]

#### 2. 普通单位
- 单位名称: [单位名称]
- 单位类型: [步兵/骑兵/法师等]
- 攻击类型: [近战/远程]
- 护甲类型: [轻甲/中甲/重甲]
- 特殊能力: [特殊能力描述]

#### 3. 建筑单位
- 建筑名称: [建筑名称]
- 建筑类型: [生产/防御/资源]
- 功能描述: [建筑功能]
- 建造条件: [建造条件]

### 单位平衡性设计

#### 数值平衡
- 生命值设计原则
- 攻击力设计原则
- 护甲设计原则
- 移动速度设计原则

#### 技能平衡
- 技能冷却时间
- 技能消耗
- 技能效果强度
- 技能组合搭配

### 单位测试清单

#### 功能测试
- [ ] 单位创建正常
- [ ] 单位移动正常
- [ ] 单位攻击正常
- [ ] 单位技能正常
- [ ] 单位死亡正常

#### 平衡性测试
- [ ] 单位数值合理
- [ ] 单位技能平衡
- [ ] 单位性价比合理
- [ ] 单位配合效果良好

### 开发建议
1. 先设计单位概念，再实现具体数值
2. 测试单位在游戏中的表现
3. 根据测试结果调整平衡性
4. 记录单位设计文档
"""
        
        unit_file = project_path / "units" / "unit_design.md"
        with open(unit_file, 'w', encoding='utf-8') as f:
            f.write(unit_template_content)
        
        print("✅ 创建单位模板完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="魔兽争霸3地图开发项目模板生成器")
    parser.add_argument("project_name", help="项目名称")
    parser.add_argument("--type", "-t", default="rpg", 
                       choices=["rpg", "td", "moba", "survival", "melee"],
                       help="项目类型")
    parser.add_argument("--author", "-a", default="", help="作者名称")
    parser.add_argument("--description", "-d", default="", help="项目描述")
    
    args = parser.parse_args()
    
    # 创建模板生成器
    generator = ProjectTemplateGenerator()
    
    # 创建项目
    success = generator.create_project(
        project_name=args.project_name,
        project_type=args.type,
        author=args.author,
        description=args.description
    )
    
    if success:
        print("\n🎉 项目创建完成！")
        print("📝 下一步:")
        print("1. 进入项目目录")
        print("2. 阅读README.md了解项目结构")
        print("3. 使用World Editor开始地图开发")
        print("4. 根据需要修改配置和文档")
    else:
        print("\n❌ 项目创建失败！")
        sys.exit(1)


if __name__ == "__main__":
    main() 