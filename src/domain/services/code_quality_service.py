#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查领域服务
负责代码质量分析和检查
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import re
import ast
import json
from datetime import datetime

from ..entities.map_project import MapProject


class QualityMetric(Enum):
    """质量指标枚举"""
    COMPLEXITY = "complexity"
    LINES_OF_CODE = "lines_of_code"
    COMMENT_RATIO = "comment_ratio"
    DUPLICATION = "duplication"
    NAMING_CONVENTION = "naming_convention"
    DOCUMENTATION = "documentation"


class QualityLevel(Enum):
    """质量级别枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class QualityIssue:
    """质量问题"""
    issue_type: str
    severity: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class QualityResult:
    """质量检查结果"""
    metric: QualityMetric
    value: float
    unit: str
    level: QualityLevel
    threshold: float
    issues: List[QualityIssue]
    timestamp: datetime
    
    @property
    def is_healthy(self) -> bool:
        """质量是否健康"""
        return self.level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]


@dataclass
class QualityReport:
    """质量报告"""
    project_name: str
    analysis_time: datetime
    overall_score: float
    metrics: List[QualityResult]
    total_issues: int
    critical_issues: int
    summary: str
    recommendations: List[str]


class CodeQualityService(ABC):
    """代码质量检查服务接口"""
    
    @abstractmethod
    def analyze_code_quality(self, project: MapProject) -> QualityReport:
        """分析代码质量"""
        pass
    
    @abstractmethod
    def get_quality_metrics(self, project: MapProject) -> List[QualityResult]:
        """获取质量指标"""
        pass
    
    @abstractmethod
    def check_specific_file(self, file_path: Path) -> List[QualityIssue]:
        """检查特定文件"""
        pass


class DefaultCodeQualityService(CodeQualityService):
    """默认代码质量检查服务实现"""
    
    def __init__(self):
        """初始化代码质量检查服务"""
        self.quality_history: List[QualityResult] = []
        self.thresholds = self._initialize_thresholds()
        self.supported_extensions = ['.py', '.js', '.lua', '.j', '.java', '.cpp', '.c', '.h']
    
    def analyze_code_quality(self, project: MapProject) -> QualityReport:
        """分析代码质量"""
        if not project.project_path.exists():
            raise ValueError(f"项目路径不存在: {project.project_path}")
        
        # 收集质量指标
        metrics = self.get_quality_metrics(project)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(metrics)
        
        # 统计问题数量
        total_issues = sum(len(m.issues) for m in metrics)
        critical_issues = sum(len([i for i in m.issues if i.severity == 'critical']) for m in metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(metrics)
        
        # 生成摘要
        summary = self._generate_summary(metrics, overall_score, total_issues, critical_issues)
        
        # 创建质量报告
        report = QualityReport(
            project_name=project.name,
            analysis_time=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            total_issues=total_issues,
            critical_issues=critical_issues,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
    
    def get_quality_metrics(self, project: MapProject) -> List[QualityResult]:
        """获取质量指标"""
        metrics = []
        
        # 复杂度指标
        complexity_metric = self._analyze_complexity(project)
        metrics.append(complexity_metric)
        
        # 代码行数指标
        loc_metric = self._analyze_lines_of_code(project)
        metrics.append(loc_metric)
        
        # 注释比例指标
        comment_ratio_metric = self._analyze_comment_ratio(project)
        metrics.append(comment_ratio_metric)
        
        # 重复代码指标
        duplication_metric = self._analyze_duplication(project)
        metrics.append(duplication_metric)
        
        # 命名规范指标
        naming_metric = self._analyze_naming_convention(project)
        metrics.append(naming_metric)
        
        # 文档完整性指标
        documentation_metric = self._analyze_documentation(project)
        metrics.append(documentation_metric)
        
        return metrics
    
    def check_specific_file(self, file_path: Path) -> List[QualityIssue]:
        """检查特定文件"""
        if not file_path.exists():
            return [QualityIssue(
                issue_type="file_not_found",
                severity="critical",
                message=f"文件不存在: {file_path}",
                file_path=str(file_path)
            )]
        
        if file_path.suffix.lower() not in self.supported_extensions:
            return [QualityIssue(
                issue_type="unsupported_file_type",
                severity="warning",
                message=f"不支持的文件类型: {file_path.suffix}",
                file_path=str(file_path)
            )]
        
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查文件大小
            if len(content) > 10000:  # 10KB
                issues.append(QualityIssue(
                    issue_type="file_too_large",
                    severity="warning",
                    message="文件过大，建议拆分为多个小文件",
                    file_path=str(file_path),
                    suggestion="将文件拆分为多个功能模块"
                ))
            
            # 检查行长度
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(QualityIssue(
                        issue_type="line_too_long",
                        severity="warning",
                        message=f"第{i}行过长 ({len(line)} 字符)",
                        file_path=str(file_path),
                        line_number=i,
                        suggestion="将长行拆分为多行"
                    ))
            
            # 检查空行
            consecutive_empty_lines = 0
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    consecutive_empty_lines += 1
                    if consecutive_empty_lines > 2:
                        issues.append(QualityIssue(
                            issue_type="too_many_empty_lines",
                            severity="info",
                            message=f"第{i}行附近空行过多",
                            file_path=str(file_path),
                            line_number=i,
                            suggestion="减少连续空行数量"
                        ))
                else:
                    consecutive_empty_lines = 0
            
            # 检查特定文件类型的质量
            if file_path.suffix.lower() == '.py':
                issues.extend(self._check_python_file(file_path, content))
            elif file_path.suffix.lower() in ['.js', '.lua']:
                issues.extend(self._check_script_file(file_path, content))
            
        except Exception as e:
            issues.append(QualityIssue(
                issue_type="parsing_error",
                severity="critical",
                message=f"解析文件时出错: {str(e)}",
                file_path=str(file_path)
            ))
        
        return issues
    
    def get_quality_history(self) -> List[QualityResult]:
        """获取质量检查历史"""
        return self.quality_history.copy()
    
    def get_quality_stats(self) -> Dict[str, Any]:
        """获取质量统计信息"""
        if not self.quality_history:
            return {
                "total_analyses": 0,
                "healthy_percentage": 0.0,
                "average_score": 0.0
            }
        
        total_analyses = len(self.quality_history)
        healthy_analyses = len([m for m in self.quality_history if m.is_healthy])
        healthy_percentage = (healthy_analyses / total_analyses) * 100
        
        # 计算平均评分
        scores = [self._metric_to_score(m) for m in self.quality_history]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_analyses": total_analyses,
            "healthy_percentage": round(healthy_percentage, 2),
            "average_score": round(average_score, 2)
        }
    
    def clear_quality_history(self) -> None:
        """清空质量检查历史"""
        self.quality_history.clear()
    
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """初始化质量阈值"""
        return {
            QualityMetric.COMPLEXITY.value: {
                "excellent": 5,
                "good": 10,
                "average": 20,
                "poor": 50,
                "critical": float('inf')
            },
            QualityMetric.LINES_OF_CODE.value: {
                "excellent": 100,
                "good": 500,
                "average": 1000,
                "poor": 5000,
                "critical": float('inf')
            },
            QualityMetric.COMMENT_RATIO.value: {
                "excellent": 0.3,
                "good": 0.2,
                "average": 0.1,
                "poor": 0.05,
                "critical": 0.0
            },
            QualityMetric.DUPLICATION.value: {
                "excellent": 0.05,
                "good": 0.1,
                "average": 0.2,
                "poor": 0.5,
                "critical": 1.0
            }
        }
    
    def _analyze_complexity(self, project: MapProject) -> QualityResult:
        """分析代码复杂度"""
        total_complexity = 0
        file_count = 0
        issues = []
        
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    complexity = self._calculate_file_complexity(file_path)
                    total_complexity += complexity
                    file_count += 1
                    
                    if complexity > 20:
                        issues.append(QualityIssue(
                            issue_type="high_complexity",
                            severity="warning",
                            message=f"文件复杂度较高: {complexity}",
                            file_path=str(file_path),
                            suggestion="重构代码，降低复杂度"
                        ))
                except Exception:
                    continue
        
        avg_complexity = total_complexity / file_count if file_count > 0 else 0
        level = self._evaluate_metric(QualityMetric.COMPLEXITY, avg_complexity)
        
        return QualityResult(
            metric=QualityMetric.COMPLEXITY,
            value=avg_complexity,
            unit="complexity",
            level=level,
            threshold=self.thresholds[QualityMetric.COMPLEXITY.value]["good"],
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _analyze_lines_of_code(self, project: MapProject) -> QualityResult:
        """分析代码行数"""
        total_lines = 0
        file_count = 0
        issues = []
        
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                        
                        if lines > 1000:
                            issues.append(QualityIssue(
                                issue_type="file_too_large",
                                severity="warning",
                                message=f"文件过大: {lines} 行",
                                file_path=str(file_path),
                                suggestion="将大文件拆分为多个小文件"
                            ))
                except Exception:
                    continue
        
        avg_lines = total_lines / file_count if file_count > 0 else 0
        level = self._evaluate_metric(QualityMetric.LINES_OF_CODE, avg_lines)
        
        return QualityResult(
            metric=QualityMetric.LINES_OF_CODE,
            value=avg_lines,
            unit="lines",
            level=level,
            threshold=self.thresholds[QualityMetric.LINES_OF_CODE.value]["good"],
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _analyze_comment_ratio(self, project: MapProject) -> QualityResult:
        """分析注释比例"""
        total_comment_ratio = 0
        file_count = 0
        issues = []
        
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    ratio = self._calculate_comment_ratio(file_path)
                    total_comment_ratio += ratio
                    file_count += 1
                    
                    if ratio < 0.1:
                        issues.append(QualityIssue(
                            issue_type="low_comment_ratio",
                            severity="warning",
                            message=f"注释比例过低: {ratio:.2%}",
                            file_path=str(file_path),
                            suggestion="增加代码注释，提高可读性"
                        ))
                except Exception:
                    continue
        
        avg_ratio = total_comment_ratio / file_count if file_count > 0 else 0
        level = self._evaluate_metric(QualityMetric.COMMENT_RATIO, avg_ratio)
        
        return QualityResult(
            metric=QualityMetric.COMMENT_RATIO,
            value=avg_ratio,
            unit="ratio",
            level=level,
            threshold=self.thresholds[QualityMetric.COMMENT_RATIO.value]["good"],
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _analyze_duplication(self, project: MapProject) -> QualityResult:
        """分析重复代码"""
        total_duplication = 0
        file_count = 0
        issues = []
        
        # 简化的重复代码检测
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    duplication = self._calculate_duplication_ratio(file_path)
                    total_duplication += duplication
                    file_count += 1
                    
                    if duplication > 0.3:
                        issues.append(QualityIssue(
                            issue_type="high_duplication",
                            severity="warning",
                            message=f"重复代码比例过高: {duplication:.2%}",
                            file_path=str(file_path),
                            suggestion="提取公共函数，减少重复代码"
                        ))
                except Exception:
                    continue
        
        avg_duplication = total_duplication / file_count if file_count > 0 else 0
        level = self._evaluate_metric(QualityMetric.DUPLICATION, avg_duplication)
        
        return QualityResult(
            metric=QualityMetric.DUPLICATION,
            value=avg_duplication,
            unit="ratio",
            level=level,
            threshold=self.thresholds[QualityMetric.DUPLICATION.value]["good"],
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _analyze_naming_convention(self, project: MapProject) -> QualityResult:
        """分析命名规范"""
        total_violations = 0
        file_count = 0
        issues = []
        
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    violations = self._check_naming_conventions(file_path)
                    total_violations += violations
                    file_count += 1
                    
                    if violations > 5:
                        issues.append(QualityIssue(
                            issue_type="naming_violations",
                            severity="warning",
                            message=f"命名规范违反: {violations} 处",
                            file_path=str(file_path),
                            suggestion="遵循命名规范，提高代码可读性"
                        ))
                except Exception:
                    continue
        
        avg_violations = total_violations / file_count if file_count > 0 else 0
        level = self._evaluate_naming_quality(avg_violations)
        
        return QualityResult(
            metric=QualityMetric.NAMING_CONVENTION,
            value=avg_violations,
            unit="violations",
            level=level,
            threshold=2.0,  # 平均违反次数阈值
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _analyze_documentation(self, project: MapProject) -> QualityResult:
        """分析文档完整性"""
        total_doc_score = 0
        file_count = 0
        issues = []
        
        for file_path in project.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    doc_score = self._calculate_documentation_score(file_path)
                    total_doc_score += doc_score
                    file_count += 1
                    
                    if doc_score < 0.5:
                        issues.append(QualityIssue(
                            issue_type="poor_documentation",
                            severity="warning",
                            message=f"文档完整性较低: {doc_score:.2%}",
                            file_path=str(file_path),
                            suggestion="完善代码文档和注释"
                        ))
                except Exception:
                    continue
        
        avg_doc_score = total_doc_score / file_count if file_count > 0 else 0
        level = self._evaluate_documentation_quality(avg_doc_score)
        
        return QualityResult(
            metric=QualityMetric.DOCUMENTATION,
            value=avg_doc_score,
            unit="score",
            level=level,
            threshold=0.7,  # 文档完整性阈值
            issues=issues,
            timestamp=datetime.now()
        )
    
    def _calculate_file_complexity(self, file_path: Path) -> int:
        """计算文件复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简化的复杂度计算
            complexity = 0
            
            # 计算条件语句
            complexity += len(re.findall(r'\bif\b|\belse\b|\bfor\b|\bwhile\b|\bcase\b', content))
            
            # 计算函数定义
            complexity += len(re.findall(r'\bdef\b|\bfunction\b|\bclass\b', content))
            
            return complexity
        except Exception:
            return 0
    
    def _calculate_comment_ratio(self, file_path: Path) -> float:
        """计算注释比例"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            comment_lines = 0
            total_lines = len(lines)
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('--'):
                    comment_lines += 1
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    comment_lines += 1
            
            return comment_lines / total_lines if total_lines > 0 else 0
        except Exception:
            return 0
    
    def _calculate_duplication_ratio(self, file_path: Path) -> float:
        """计算重复代码比例"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 简化的重复代码检测
            unique_lines = set()
            total_lines = len(lines)
            
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    unique_lines.add(stripped)
            
            return 1 - (len(unique_lines) / total_lines) if total_lines > 0 else 0
        except Exception:
            return 0
    
    def _check_naming_conventions(self, file_path: Path) -> int:
        """检查命名规范"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            violations = 0
            
            # 检查变量命名（应该使用小写字母和下划线）
            variables = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*=', content)
            for var in variables:
                var_name = var.split('=')[0].strip()
                if re.match(r'^[A-Z][a-zA-Z0-9_]*$', var_name):  # 首字母大写
                    violations += 1
            
            # 检查函数命名
            functions = re.findall(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
            for func in functions:
                if not re.match(r'^[a-z_][a-z0-9_]*$', func):  # 应该使用小写
                    violations += 1
            
            return violations
        except Exception:
            return 0
    
    def _calculate_documentation_score(self, file_path: Path) -> float:
        """计算文档完整性评分"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            score = 0.0
            
            # 检查文件头注释
            if re.search(r'^#.*\n#.*\n#.*', content, re.MULTILINE):
                score += 0.2
            
            # 检查函数文档字符串
            functions = re.findall(r'\bdef\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(', content)
            docstrings = re.findall(r'"""[^"]*"""|\'\'\'[^\']*\'\'\'', content)
            
            if functions:
                doc_ratio = len(docstrings) / len(functions)
                score += min(doc_ratio * 0.5, 0.5)
            
            # 检查行内注释
            comment_lines = len(re.findall(r'#.*$', content, re.MULTILINE))
            total_lines = len(content.split('\n'))
            
            if total_lines > 0:
                comment_ratio = comment_lines / total_lines
                score += min(comment_ratio * 0.3, 0.3)
            
            return score
        except Exception:
            return 0.0
    
    def _evaluate_metric(self, metric: QualityMetric, value: float) -> QualityLevel:
        """评估指标质量级别"""
        thresholds = self.thresholds[metric.value]
        
        if value <= thresholds["excellent"]:
            return QualityLevel.EXCELLENT
        elif value <= thresholds["good"]:
            return QualityLevel.GOOD
        elif value <= thresholds["average"]:
            return QualityLevel.AVERAGE
        elif value <= thresholds["poor"]:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _evaluate_naming_quality(self, violations: float) -> QualityLevel:
        """评估命名质量"""
        if violations <= 1:
            return QualityLevel.EXCELLENT
        elif violations <= 3:
            return QualityLevel.GOOD
        elif violations <= 5:
            return QualityLevel.AVERAGE
        elif violations <= 10:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _evaluate_documentation_quality(self, score: float) -> QualityLevel:
        """评估文档质量"""
        if score >= 0.8:
            return QualityLevel.EXCELLENT
        elif score >= 0.6:
            return QualityLevel.GOOD
        elif score >= 0.4:
            return QualityLevel.AVERAGE
        elif score >= 0.2:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _calculate_overall_score(self, metrics: List[QualityResult]) -> float:
        """计算总体评分"""
        if not metrics:
            return 0.0
        
        scores = [self._metric_to_score(metric) for metric in metrics]
        return sum(scores) / len(scores)
    
    def _metric_to_score(self, metric: QualityResult) -> float:
        """将质量级别转换为分数"""
        score_map = {
            QualityLevel.EXCELLENT: 100,
            QualityLevel.GOOD: 80,
            QualityLevel.AVERAGE: 60,
            QualityLevel.POOR: 40,
            QualityLevel.CRITICAL: 20
        }
        return score_map.get(metric.level, 0)
    
    def _generate_recommendations(self, metrics: List[QualityResult]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for metric in metrics:
            if not metric.is_healthy:
                for issue in metric.issues:
                    recommendations.append(f"{metric.metric.value}: {issue.suggestion}")
        
        if not recommendations:
            recommendations.append("代码质量良好，无需特殊优化")
        
        return recommendations
    
    def _generate_summary(self, metrics: List[QualityResult], overall_score: float, 
                         total_issues: int, critical_issues: int) -> str:
        """生成质量摘要"""
        healthy_count = len([m for m in metrics if m.is_healthy])
        total_count = len(metrics)
        
        if overall_score >= 90:
            status = "优秀"
        elif overall_score >= 80:
            status = "良好"
        elif overall_score >= 60:
            status = "一般"
        elif overall_score >= 40:
            status = "较差"
        else:
            status = "严重"
        
        return (f"代码质量状态：{status}，总体评分：{overall_score:.1f}，"
                f"健康指标：{healthy_count}/{total_count}，"
                f"总问题数：{total_issues}，严重问题：{critical_issues}")
    
    def _check_python_file(self, file_path: Path, content: str) -> List[QualityIssue]:
        """检查Python文件质量"""
        issues = []
        
        try:
            # 尝试解析Python代码
            ast.parse(content)
        except SyntaxError as e:
            issues.append(QualityIssue(
                issue_type="syntax_error",
                severity="critical",
                message=f"语法错误: {str(e)}",
                file_path=str(file_path),
                line_number=getattr(e, 'lineno', None),
                suggestion="修复语法错误"
            ))
        
        # 检查导入语句
        import_lines = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
        if len(import_lines) > 10:
            issues.append(QualityIssue(
                issue_type="too_many_imports",
                severity="warning",
                message=f"导入语句过多: {len(import_lines)} 个",
                file_path=str(file_path),
                suggestion="整理导入语句，删除未使用的导入"
            ))
        
        return issues
    
    def _check_script_file(self, file_path: Path, content: str) -> List[QualityIssue]:
        """检查脚本文件质量"""
        issues = []
        
        # 检查魔法数字
        magic_numbers = re.findall(r'\b\d{4,}\b', content)
        if magic_numbers:
            issues.append(QualityIssue(
                issue_type="magic_numbers",
                severity="info",
                message=f"发现魔法数字: {len(magic_numbers)} 个",
                file_path=str(file_path),
                suggestion="将魔法数字定义为常量"
            ))
        
        return issues
