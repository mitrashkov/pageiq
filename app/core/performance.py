"""
Performance monitoring and profiling utilities
"""

import asyncio
import cProfile
import io
import pstats
import threading
import time
import tracemalloc
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
import psutil
import os

from app.core.config import settings
from app.core.sentry import alert_manager


class PerformanceMonitor:
    """Performance monitoring and profiling service"""

    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time_ms': 5000,
        }

    def start_monitoring(self, interval: int = 60):
        """Start background performance monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self, interval: int):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self.collect_system_metrics()

                # Store metrics history (keep last 100 entries)
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)

                # Check for alerts
                self._check_alerts(metrics)

                time.sleep(interval)
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(interval)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # Network metrics (basic)
            network = psutil.net_io_counters()
            bytes_sent_mb = network.bytes_sent / (1024 * 1024)
            bytes_recv_mb = network.bytes_recv / (1024 * 1024)

            # Process metrics
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            process_cpu_percent = process.cpu_percent()

            return {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_mb': memory_used_mb,
                'disk_percent': disk_percent,
                'network_sent_mb': bytes_sent_mb,
                'network_recv_mb': bytes_recv_mb,
                'process_memory_mb': process_memory_mb,
                'process_cpu_percent': process_cpu_percent,
            }
        except Exception as e:
            return {
                'timestamp': time.time(),
                'error': str(e)
            }

    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against alert thresholds"""
        alerts = []

        if metrics.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']}%")

        if metrics.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {metrics['memory_percent']}%")

        for alert in alerts:
            alert_manager.alert_performance_degradation(
                metric=alert.split(':')[0],
                threshold=self.alert_thresholds.get(alert.split(':')[0].lower().replace(' ', '_'), 'unknown')
            )

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}

        # Calculate averages and peaks
        cpu_values = [m.get('cpu_percent', 0) for m in self.metrics_history if 'cpu_percent' in m]
        memory_values = [m.get('memory_percent', 0) for m in self.metrics_history if 'memory_percent' in m]

        return {
            'current': self.metrics_history[-1] if self.metrics_history else {},
            'averages': {
                'cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'memory_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
            },
            'peaks': {
                'cpu_percent': max(cpu_values) if cpu_values else 0,
                'memory_percent': max(memory_values) if memory_values else 0,
            },
            'sample_count': len(self.metrics_history),
            'alert_thresholds': self.alert_thresholds,
        }


class Profiler:
    """Code profiling utilities"""

    @staticmethod
    @contextmanager
    def profile_code(name: str = "code_block", print_results: bool = False):
        """Profile a block of code"""
        pr = cProfile.Profile()
        pr.enable()

        try:
            yield
        finally:
            pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()

            profile_data = s.getvalue()

            if print_results:
                print(f"Profile results for {name}:")
                print(profile_data)

            # Could save to file or send to monitoring system
            # For now, just log the top 10 functions
            lines = profile_data.split('\n')
            if len(lines) > 15:  # Has meaningful data
                top_functions = '\n'.join(lines[:15])
                print(f"Top functions in {name}:\n{top_functions}")

    @staticmethod
    @contextmanager
    def trace_memory(name: str = "memory_block", print_results: bool = False):
        """Trace memory usage for a block of code"""
        tracemalloc.start()

        try:
            yield
        finally:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            memory_info = f"Memory usage for {name}: Current={current/1024/1024:.1f}MB, Peak={peak/1024/1024:.1f}MB"

            if print_results:
                print(memory_info)

            # Check for memory leaks
            if peak > 100 * 1024 * 1024:  # 100MB
                alert_manager.alert_performance_degradation(
                    metric="memory_usage",
                    threshold="100MB"
                )


class APMMiddleware:
    """Application Performance Monitoring middleware"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Track request performance
        start_time = time.time()
        request_size = 0

        # Capture request body size
        original_receive = receive
        async def receive_with_tracking():
            nonlocal request_size
            message = await original_receive()
            if message["type"] == "http.request":
                request_size += len(message.get("body", b""))
            return message

        # Process request
        response_size = 0
        response_status = 200

        async def send_with_tracking(message):
            nonlocal response_size, response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_size += len(message.get("body", b""))
            await send(message)

        await self.app(scope, receive_with_tracking, send_with_tracking)

        # Record performance metrics
        processing_time = (time.time() - start_time) * 1000

        # Check for slow requests
        if processing_time > 5000:  # 5 seconds
            alert_manager.alert_performance_degradation(
                metric="response_time",
                threshold="5000ms"
            )


# Global instances
performance_monitor = PerformanceMonitor()
profiler = Profiler()