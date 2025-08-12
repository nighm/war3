#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析领域服务
负责地图项目的性能分析和监控
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time
import psutil
import os
from datetime import datetime

from ..entities.map_project import MapProject


class PerformanceMetric(Enum):
    """性能指标枚举"""
    FILE_SIZE = "file_size"
    FILE_COUNT = "file_count"
    MEMORY_USAGE = "memory_usage"
    PROCESSING_TIME = "processing_time"
    CPU_USAGE = "cpu_usage"
    DISK_IO = "disk_io"


class PerformanceLevel(Enum):
    """性能级别枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceResult:
    """性能分析结果"""
    metric: PerformanceMetric
    value: float
    unit: str
    level: PerformanceLevel
    threshold: float
    recommendation: str
    timestamp: datetime
    
    @property
    def is_healthy(self) -> bool:
        """性能是否健康"""
        return self.level in [PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD]


@dataclass
class PerformanceReport:
    """性能报告"""
    project_name: str
    analysis_time: datetime
    overall_score: float
    metrics: List[PerformanceResult]
    summary: str
    recommendations: List[str]


class PerformanceAnalysisService(ABC):
    """性能分析服务接口"""
    
    @abstractmethod
    def analyze_project_performance(self, project: MapProject) -> PerformanceReport:
        """分析项目性能"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self, project: MapProject) -> List[PerformanceResult]:
        """获取性能指标"""
        pass
    
    @abstractmethod
    def monitor_performance(self, project: MapProject, 
                           duration: int = 60) -> List[PerformanceResult]:
        """监控性能"""
        pass


class DefaultPerformanceAnalysisService(PerformanceAnalysisService):
    """默认性能分析服务实现"""
    
    def __init__(self):
        """初始化性能分析服务"""
        self.performance_history: List[PerformanceResult] = []
        self.thresholds = self._initialize_thresholds()
    
    def analyze_project_performance(self, project: MapProject) -> PerformanceReport:
        """分析项目性能"""
        if not project.project_path.exists():
            raise ValueError(f"项目路径不存在: {project.project_path}")
        
        # 收集性能指标
        metrics = self.get_performance_metrics(project)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(metrics)
        
        # 生成建议
        recommendations = self._generate_recommendations(metrics)
        
        # 生成摘要
        summary = self._generate_summary(metrics, overall_score)
        
        # 创建性能报告
        report = PerformanceReport(
            project_name=project.name,
            analysis_time=datetime.now(),
            overall_score=overall_score,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
    
    def get_performance_metrics(self, project: MapProject) -> List[PerformanceResult]:
        """获取性能指标"""
        metrics = []
        
        # 文件大小指标
        file_size_metric = self._analyze_file_size(project)
        metrics.append(file_size_metric)
        
        # 文件数量指标
        file_count_metric = self._analyze_file_count(project)
        metrics.append(file_count_metric)
        
        # 内存使用指标
        memory_metric = self._analyze_memory_usage(project)
        metrics.append(memory_metric)
        
        # 磁盘IO指标
        disk_io_metric = self._analyze_disk_io(project)
        metrics.append(disk_io_metric)
        
        # 处理时间指标
        processing_time_metric = self._analyze_processing_time(project)
        metrics.append(processing_time_metric)
        
        return metrics
    
    def monitor_performance(self, project: MapProject, 
                           duration: int = 60) -> List[PerformanceResult]:
        """监控性能"""
        if not project.project_path.exists():
            raise ValueError(f"项目路径不存在: {project.project_path}")
        
        monitoring_results = []
        start_time = time.time()
        
        print(f"开始监控项目 '{project.name}' 性能，持续 {duration} 秒...")
        
        while time.time() - start_time < duration:
            # 收集当前性能指标
            current_metrics = self.get_performance_metrics(project)
            
            # 记录监控结果
            for metric in current_metrics:
                monitoring_results.append(metric)
                self.performance_history.append(metric)
            
            # 显示实时状态
            self._display_monitoring_status(current_metrics, time.time() - start_time)
            
            # 等待1秒
            time.sleep(1)
        
        print(f"性能监控完成，共收集 {len(monitoring_results)} 个数据点")
        return monitoring_results
    
    def get_performance_history(self) -> List[PerformanceResult]:
        """获取性能历史"""
        return self.performance_history.copy()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        if not self.performance_history:
            return {
                "total_measurements": 0,
                "healthy_percentage": 0.0,
                "average_score": 0.0
            }
        
        total_measurements = len(self.performance_history)
        healthy_measurements = len([m for m in self.performance_history if m.is_healthy])
        healthy_percentage = (healthy_measurements / total_measurements) * 100
        
        # 计算平均评分
        scores = [self._metric_to_score(m) for m in self.performance_history]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "total_measurements": total_measurements,
            "healthy_percentage": round(healthy_percentage, 2),
            "average_score": round(average_score, 2),
            "monitoring_duration_hours": round(total_measurements / 3600, 2)
        }
    
    def clear_performance_history(self) -> None:
        """清空性能历史"""
        self.performance_history.clear()
    
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """初始化性能阈值"""
        return {
            PerformanceMetric.FILE_SIZE.value: {
                "excellent": 50 * 1024 * 1024,    # 50MB
                "good": 100 * 1024 * 1024,        # 100MB
                "average": 500 * 1024 * 1024,     # 500MB
                "poor": 1024 * 1024 * 1024,       # 1GB
                "critical": float('inf')
            },
            PerformanceMetric.FILE_COUNT.value: {
                "excellent": 100,
                "good": 500,
                "average": 1000,
                "poor": 5000,
                "critical": float('inf')
            },
            PerformanceMetric.MEMORY_USAGE.value: {
                "excellent": 50 * 1024 * 1024,    # 50MB
                "good": 100 * 1024 * 1024,        # 100MB
                "average": 500 * 1024 * 1024,     # 500MB
                "poor": 1024 * 1024 * 1024,       # 1GB
                "critical": float('inf')
            },
            PerformanceMetric.PROCESSING_TIME.value: {
                "excellent": 1.0,                  # 1秒
                "good": 5.0,                       # 5秒
                "average": 15.0,                   # 15秒
                "poor": 60.0,                      # 1分钟
                "critical": float('inf')
            }
        }
    
    def _analyze_file_size(self, project: MapProject) -> PerformanceResult:
        """分析文件大小性能"""
        total_size = self._calculate_project_size(project.project_path)
        size_mb = total_size / (1024 * 1024)
        
        level = self._evaluate_metric(PerformanceMetric.FILE_SIZE, total_size)
        recommendation = self._get_file_size_recommendation(size_mb)
        
        return PerformanceResult(
            metric=PerformanceMetric.FILE_SIZE,
            value=size_mb,
            unit="MB",
            level=level,
            threshold=self.thresholds[PerformanceMetric.FILE_SIZE.value]["good"] / (1024 * 1024),
            recommendation=recommendation,
            timestamp=datetime.now()
        )
    
    def _analyze_file_count(self, project: MapProject) -> PerformanceResult:
        """分析文件数量性能"""
        file_count = self._count_project_files(project.project_path)
        
        level = self._evaluate_metric(PerformanceMetric.FILE_COUNT, file_count)
        recommendation = self._get_file_count_recommendation(file_count)
        
        return PerformanceResult(
            metric=PerformanceMetric.FILE_COUNT,
            value=file_count,
            unit="files",
            level=level,
            threshold=self.thresholds[PerformanceMetric.FILE_COUNT.value]["good"],
            recommendation=recommendation,
            timestamp=datetime.now()
        )
    
    def _analyze_memory_usage(self, project: MapProject) -> PerformanceResult:
        """分析内存使用性能"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            level = self._evaluate_metric(PerformanceMetric.MEMORY_USAGE, memory_info.rss)
            recommendation = self._get_memory_recommendation(memory_mb)
            
            return PerformanceResult(
                metric=PerformanceMetric.MEMORY_USAGE,
                value=memory_mb,
                unit="MB",
                level=level,
                threshold=self.thresholds[PerformanceMetric.MEMORY_USAGE.value]["good"] / (1024 * 1024),
                recommendation=recommendation,
                timestamp=datetime.now()
            )
        except Exception:
            # 如果无法获取内存信息，返回默认值
            return PerformanceResult(
                metric=PerformanceMetric.MEMORY_USAGE,
                value=0.0,
                unit="MB",
                level=PerformanceLevel.AVERAGE,
                threshold=0.0,
                recommendation="无法获取内存使用信息",
                timestamp=datetime.now()
            )
    
    def _analyze_disk_io(self, project: MapProject) -> PerformanceResult:
        """分析磁盘IO性能"""
        try:
            disk_usage = psutil.disk_usage(project.project_path)
            free_space_gb = disk_usage.free / (1024 * 1024 * 1024)
            
            # 根据可用空间评估性能
            if free_space_gb > 10:
                level = PerformanceLevel.EXCELLENT
            elif free_space_gb > 5:
                level = PerformanceLevel.GOOD
            elif free_space_gb > 1:
                level = PerformanceLevel.AVERAGE
            elif free_space_gb > 0.5:
                level = PerformanceLevel.POOR
            else:
                level = PerformanceLevel.CRITICAL
            
            recommendation = self._get_disk_io_recommendation(free_space_gb)
            
            return PerformanceResult(
                metric=PerformanceMetric.DISK_IO,
                value=free_space_gb,
                unit="GB",
                level=level,
                threshold=5.0,  # 5GB
                recommendation=recommendation,
                timestamp=datetime.now()
            )
        except Exception:
            return PerformanceResult(
                metric=PerformanceMetric.DISK_IO,
                value=0.0,
                unit="GB",
                level=PerformanceLevel.AVERAGE,
                threshold=0.0,
                recommendation="无法获取磁盘使用信息",
                timestamp=datetime.now()
            )
    
    def _analyze_processing_time(self, project: MapProject) -> PerformanceResult:
        """分析处理时间性能"""
        start_time = time.time()
        
        # 模拟一些处理操作
        self._simulate_processing(project)
        
        processing_time = time.time() - start_time
        
        level = self._evaluate_metric(PerformanceMetric.PROCESSING_TIME, processing_time)
        recommendation = self._get_processing_time_recommendation(processing_time)
        
        return PerformanceResult(
            metric=PerformanceMetric.PROCESSING_TIME,
            value=processing_time,
            unit="seconds",
            level=level,
            threshold=self.thresholds[PerformanceMetric.PROCESSING_TIME.value]["good"],
            recommendation=recommendation,
            timestamp=datetime.now()
        )
    
    def _evaluate_metric(self, metric: PerformanceMetric, value: float) -> PerformanceLevel:
        """评估指标性能级别"""
        thresholds = self.thresholds[metric.value]
        
        if value <= thresholds["excellent"]:
            return PerformanceLevel.EXCELLENT
        elif value <= thresholds["good"]:
            return PerformanceLevel.GOOD
        elif value <= thresholds["average"]:
            return PerformanceLevel.AVERAGE
        elif value <= thresholds["poor"]:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def _calculate_overall_score(self, metrics: List[PerformanceResult]) -> float:
        """计算总体评分"""
        if not metrics:
            return 0.0
        
        scores = [self._metric_to_score(metric) for metric in metrics]
        return sum(scores) / len(scores)
    
    def _metric_to_score(self, metric: PerformanceResult) -> float:
        """将性能级别转换为分数"""
        score_map = {
            PerformanceLevel.EXCELLENT: 100,
            PerformanceLevel.GOOD: 80,
            PerformanceLevel.AVERAGE: 60,
            PerformanceLevel.POOR: 40,
            PerformanceLevel.CRITICAL: 20
        }
        return score_map.get(metric.level, 0)
    
    def _generate_recommendations(self, metrics: List[PerformanceResult]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for metric in metrics:
            if not metric.is_healthy:
                recommendations.append(f"{metric.metric.value}: {metric.recommendation}")
        
        if not recommendations:
            recommendations.append("项目性能良好，无需特殊优化")
        
        return recommendations
    
    def _generate_summary(self, metrics: List[PerformanceResult], overall_score: float) -> str:
        """生成性能摘要"""
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
        
        return f"项目性能状态：{status}，总体评分：{overall_score:.1f}，健康指标：{healthy_count}/{total_count}"
    
    def _display_monitoring_status(self, metrics: List[PerformanceResult], elapsed_time: float):
        """显示监控状态"""
        print(f"\r监控中... {elapsed_time:.1f}s | ", end="")
        
        for metric in metrics:
            status_icon = "✅" if metric.is_healthy else "⚠️"
            print(f"{metric.metric.value}: {metric.value:.1f}{metric.unit} {status_icon} | ", end="")
        
        print("", end="", flush=True)
    
    def _calculate_project_size(self, path: Path) -> int:
        """计算项目大小（字节）"""
        try:
            return sum(
                f.stat().st_size for f in path.rglob("*") 
                if f.is_file()
            )
        except Exception:
            return 0
    
    def _count_project_files(self, path: Path) -> int:
        """计算项目文件数量"""
        try:
            return len([f for f in path.rglob("*") if f.is_file()])
        except Exception:
            return 0
    
    def _simulate_processing(self, project: MapProject) -> None:
        """模拟处理操作"""
        # 模拟文件扫描
        if project.project_path.exists():
            list(project.project_path.rglob("*"))
    
    def _get_file_size_recommendation(self, size_mb: float) -> str:
        """获取文件大小建议"""
        if size_mb > 1000:
            return "项目过大，建议压缩资源文件或删除不必要的文件"
        elif size_mb > 500:
            return "项目较大，建议优化资源文件"
        elif size_mb > 100:
            return "项目大小适中，建议定期清理临时文件"
        else:
            return "项目大小合理，无需特殊处理"
    
    def _get_file_count_recommendation(self, file_count: int) -> str:
        """获取文件数量建议"""
        if file_count > 5000:
            return "文件数量过多，建议整理和合并小文件"
        elif file_count > 1000:
            return "文件数量较多，建议按功能分组"
        else:
            return "文件数量合理，结构清晰"
    
    def _get_memory_recommendation(self, memory_mb: float) -> str:
        """获取内存使用建议"""
        if memory_mb > 1000:
            return "内存使用过高，建议优化算法或增加内存"
        elif memory_mb > 500:
            return "内存使用较高，建议检查内存泄漏"
        else:
            return "内存使用合理"
    
    def _get_disk_io_recommendation(self, free_space_gb: float) -> str:
        """获取磁盘IO建议"""
        if free_space_gb < 1:
            return "磁盘空间严重不足，建议立即清理或扩容"
        elif free_space_gb < 5:
            return "磁盘空间不足，建议清理临时文件"
        else:
            return "磁盘空间充足"
    
    def _get_processing_time_recommendation(self, processing_time: float) -> str:
        """获取处理时间建议"""
        if processing_time > 60:
            return "处理时间过长，建议优化算法或使用缓存"
        elif processing_time > 15:
            return "处理时间较长，建议检查性能瓶颈"
        else:
            return "处理时间合理"
