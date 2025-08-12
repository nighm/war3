#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控服务
监控和分析系统性能，提供优化建议
"""

import time
import psutil
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import json


@dataclass
class PerformanceMetric:
    """性能指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int
    active_threads: int
    open_files: int


@dataclass
class PerformanceAlert:
    """性能告警"""
    level: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    metric: str
    current_value: float
    threshold: float
    recommendation: str


@dataclass
class PerformanceReport:
    """性能报告"""
    start_time: datetime
    end_time: datetime
    metrics: List[PerformanceMetric]
    alerts: List[PerformanceAlert]
    summary: Dict[str, float]
    recommendations: List[str]


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.metrics: List[PerformanceMetric] = []
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # 性能阈值
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_io_read": 1000000,  # 1MB/s
            "disk_io_write": 1000000,  # 1MB/s
            "network_sent": 1000000,   # 1MB/s
            "network_recv": 1000000,   # 1MB/s
            "active_threads": 100,
            "open_files": 1000
        }
    
    def start_monitoring(self) -> None:
        """开始性能监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitoring_loop(self) -> None:
        """监控循环"""
        while self.is_monitoring:
            try:
                metric = self._collect_metric()
                self.metrics.append(metric)
                
                # 检查告警
                alert = self._check_alerts(metric)
                if alert:
                    self.alerts.append(alert)
                    self._notify_alerts(alert)
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"性能监控错误: {e}")
    
    def _collect_metric(self) -> PerformanceMetric:
        """收集性能指标"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network = psutil.net_io_counters()
        
        return PerformanceMetric(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io_read=disk_io.read_bytes if disk_io else 0,
            disk_io_write=disk_io.write_bytes if disk_io else 0,
            network_sent=network.bytes_sent if network else 0,
            network_recv=network.bytes_recv if network else 0,
            active_threads=threading.active_count(),
            open_files=len(psutil.Process().open_files())
        )
    
    def _check_alerts(self, metric: PerformanceMetric) -> Optional[PerformanceAlert]:
        """检查性能告警"""
        for metric_name, threshold in self.thresholds.items():
            current_value = getattr(metric, metric_name)
            
            if current_value > threshold:
                level = self._determine_alert_level(current_value, threshold)
                recommendation = self._get_recommendation(metric_name, current_value, threshold)
                
                return PerformanceAlert(
                    level=level,
                    message=f"{metric_name} 超过阈值: {current_value:.2f} > {threshold:.2f}",
                    timestamp=metric.timestamp,
                    metric=metric_name,
                    current_value=current_value,
                    threshold=threshold,
                    recommendation=recommendation
                )
        
        return None
    
    def _determine_alert_level(self, current_value: float, threshold: float) -> str:
        """确定告警级别"""
        ratio = current_value / threshold
        if ratio > 2.0:
            return "critical"
        elif ratio > 1.5:
            return "high"
        elif ratio > 1.2:
            return "medium"
        else:
            return "low"
    
    def _get_recommendation(self, metric_name: str, current_value: float, threshold: float) -> str:
        """获取优化建议"""
        recommendations = {
            "cpu_percent": "考虑优化算法或增加CPU核心",
            "memory_percent": "检查内存泄漏，考虑增加内存或优化数据结构",
            "disk_io_read": "优化文件读取策略，考虑缓存机制",
            "disk_io_write": "优化文件写入策略，考虑批量写入",
            "network_sent": "优化网络传输，考虑压缩或减少传输频率",
            "network_recv": "优化网络接收，考虑缓存或减少请求频率",
            "active_threads": "检查线程池配置，避免创建过多线程",
            "open_files": "及时关闭文件句柄，检查文件资源管理"
        }
        
        return recommendations.get(metric_name, "建议检查系统配置")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)
    
    def _notify_alerts(self, alert: PerformanceAlert) -> None:
        """通知告警"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"告警回调执行错误: {e}")
    
    def get_performance_summary(self) -> Dict[str, float]:
        """获取性能摘要"""
        if not self.metrics:
            return {}
        
        latest_metric = self.metrics[-1]
        return {
            "cpu_percent": latest_metric.cpu_percent,
            "memory_percent": latest_metric.memory_percent,
            "disk_io_read_mb": latest_metric.disk_io_read / 1024 / 1024,
            "disk_io_write_mb": latest_metric.disk_io_write / 1024 / 1024,
            "network_sent_mb": latest_metric.network_sent / 1024 / 1024,
            "network_recv_mb": latest_metric.network_recv / 1024 / 1024,
            "active_threads": latest_metric.active_threads,
            "open_files": latest_metric.open_files
        }
    
    def generate_report(self, start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None) -> PerformanceReport:
        """生成性能报告"""
        if not start_time:
            start_time = self.metrics[0].timestamp if self.metrics else datetime.now()
        if not end_time:
            end_time = datetime.now()
        
        # 过滤时间范围内的指标
        filtered_metrics = [
            m for m in self.metrics 
            if start_time <= m.timestamp <= end_time
        ]
        
        # 过滤时间范围内的告警
        filtered_alerts = [
            a for a in self.alerts 
            if start_time <= a.timestamp <= end_time
        ]
        
        # 计算摘要统计
        if filtered_metrics:
            summary = {
                "avg_cpu_percent": sum(m.cpu_percent for m in filtered_metrics) / len(filtered_metrics),
                "max_cpu_percent": max(m.cpu_percent for m in filtered_metrics),
                "avg_memory_percent": sum(m.memory_percent for m in filtered_metrics) / len(filtered_metrics),
                "max_memory_percent": max(m.memory_percent for m in filtered_metrics),
                "total_disk_read_mb": sum(m.disk_io_read for m in filtered_metrics) / 1024 / 1024,
                "total_disk_write_mb": sum(m.disk_io_write for m in filtered_metrics) / 1024 / 1024,
                "total_network_sent_mb": sum(m.network_sent for m in filtered_metrics) / 1024 / 1024,
                "total_network_recv_mb": sum(m.network_recv for m in filtered_metrics) / 1024 / 1024
            }
        else:
            summary = {}
        
        # 生成优化建议
        recommendations = self._generate_recommendations(filtered_metrics, filtered_alerts)
        
        return PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            metrics=filtered_metrics,
            alerts=filtered_alerts,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric], 
                                 alerts: List[PerformanceAlert]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if not metrics:
            return recommendations
        
        # CPU使用率建议
        avg_cpu = sum(m.cpu_percent for m in metrics) / len(metrics)
        if avg_cpu > 70:
            recommendations.append("CPU使用率较高，建议优化算法或增加CPU核心")
        
        # 内存使用率建议
        avg_memory = sum(m.memory_percent for m in metrics) / len(metrics)
        if avg_memory > 80:
            recommendations.append("内存使用率较高，建议检查内存泄漏或增加内存")
        
        # 磁盘IO建议
        total_disk_read = sum(m.disk_io_read for m in metrics)
        total_disk_write = sum(m.disk_io_write for m in metrics)
        if total_disk_read > 100 * 1024 * 1024:  # 100MB
            recommendations.append("磁盘读取量较大，建议优化文件读取策略或增加缓存")
        if total_disk_write > 100 * 1024 * 1024:  # 100MB
            recommendations.append("磁盘写入量较大，建议优化文件写入策略或批量写入")
        
        # 网络IO建议
        total_network_sent = sum(m.network_sent for m in metrics)
        total_network_recv = sum(m.network_recv for m in metrics)
        if total_network_sent > 50 * 1024 * 1024:  # 50MB
            recommendations.append("网络发送量较大，建议优化网络传输或减少传输频率")
        if total_network_recv > 50 * 1024 * 1024:  # 50MB
            recommendations.append("网络接收量较大，建议优化网络接收或增加缓存")
        
        # 线程数量建议
        max_threads = max(m.active_threads for m in metrics)
        if max_threads > 50:
            recommendations.append("活跃线程数量较多，建议优化线程池配置或减少并发")
        
        # 文件句柄建议
        max_files = max(m.open_files for m in metrics)
        if max_files > 500:
            recommendations.append("打开文件数量较多，建议及时关闭文件句柄或优化文件管理")
        
        return recommendations
    
    def save_metrics(self, file_path: str) -> None:
        """保存性能指标到文件"""
        data = {
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "disk_io_read": m.disk_io_read,
                    "disk_io_write": m.disk_io_write,
                    "network_sent": m.network_sent,
                    "network_recv": m.network_recv,
                    "active_threads": m.active_threads,
                    "open_files": m.open_files
                }
                for m in self.metrics
            ],
            "alerts": [
                {
                    "level": a.level,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                    "metric": a.metric,
                    "current_value": a.current_value,
                    "threshold": a.threshold,
                    "recommendation": a.recommendation
                }
                for a in self.alerts
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_metrics(self, file_path: str) -> None:
        """从文件加载性能指标"""
        if not Path(file_path).exists():
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载指标
        self.metrics = []
        for m_data in data.get("metrics", []):
            metric = PerformanceMetric(
                timestamp=datetime.fromisoformat(m_data["timestamp"]),
                cpu_percent=m_data["cpu_percent"],
                memory_percent=m_data["memory_percent"],
                disk_io_read=m_data["disk_io_read"],
                disk_io_write=m_data["disk_io_write"],
                network_sent=m_data["network_sent"],
                network_recv=m_data["network_recv"],
                active_threads=m_data["active_threads"],
                open_files=m_data["open_files"]
            )
            self.metrics.append(metric)
        
        # 加载告警
        self.alerts = []
        for a_data in data.get("alerts", []):
            alert = PerformanceAlert(
                level=a_data["level"],
                message=a_data["message"],
                timestamp=datetime.fromisoformat(a_data["timestamp"]),
                metric=a_data["metric"],
                current_value=a_data["current_value"],
                threshold=a_data["threshold"],
                recommendation=a_data["recommendation"]
            )
            self.alerts.append(alert)
    
    def clear_metrics(self) -> None:
        """清除性能指标"""
        self.metrics.clear()
        self.alerts.clear()
