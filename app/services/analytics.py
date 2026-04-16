import logging
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking and analyzing API usage patterns"""

    def __init__(self):
        self.redis = get_redis()

    def track_request(
        self,
        user_id: Optional[str],
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """
        Track an API request for analytics

        Args:
            user_id: User identifier (if authenticated)
            endpoint: API endpoint called
            method: HTTP method
            response_time: Response time in milliseconds
            status_code: HTTP status code
            user_agent: User agent string
            ip_address: Client IP address
        """
        try:
            current_time = datetime.utcnow()
            date_key = current_time.strftime("%Y-%m-%d")
            hour_key = current_time.strftime("%Y-%m-%d-%H")

            # Track various metrics
            self._increment_counter(f"requests:total:{date_key}")
            self._increment_counter(f"requests:endpoint:{endpoint}:{date_key}")
            self._increment_counter(f"requests:method:{method}:{date_key}")
            self._increment_counter(f"requests:status:{status_code}:{date_key}")

            if user_id:
                self._increment_counter(f"requests:user:{user_id}:{date_key}")

            # Track response time histogram
            self._add_to_histogram(f"response_time:{endpoint}:{date_key}", response_time)

            # Track user agents (top 10)
            if user_agent:
                self._track_top_items(f"user_agents:{date_key}", user_agent, 10)

            # Expire old data (keep 30 days)
            self._expire_old_data(date_key)

        except Exception as e:
            logger.error(f"Error tracking analytics: {str(e)}")

    def track_analyzed_url(self, analyzed_url: str) -> None:
        """Track domains being analyzed (called from the analyze handler)."""
        try:
            current_time = datetime.utcnow()
            date_key = current_time.strftime("%Y-%m-%d")
            host = urlparse(analyzed_url).hostname or ""
            if not host:
                return
            host = host.lower()
            self._track_top_items(f"analyzed_domains:{date_key}", host, 50)
            self.redis.expire(f"analyzed_domains:{date_key}", 30 * 24 * 60 * 60)
        except Exception as e:
            logger.error(f"Error tracking analyzed url: {str(e)}")

    def get_usage_stats(
        self,
        days: int = 7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics

        Args:
            days: Number of days to look back
            user_id: Specific user to get stats for

        Returns:
            Dictionary with usage statistics
        """
        try:
            stats = {
                "period_days": days,
                "total_requests": 0,
                "requests_by_endpoint": {},
                "requests_by_status": {},
                "average_response_time": 0.0,
                "top_endpoints": [],
                "top_user_agents": []
            }

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            total_requests = 0
            total_response_time = 0.0
            response_time_count = 0

            # Aggregate data across date range
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")

                # Total requests
                requests_key = f"requests:user:{user_id}:{date_key}" if user_id else f"requests:total:{date_key}"
                day_requests = int(self.redis.get(requests_key) or 0)
                total_requests += day_requests

                # Requests by endpoint
                endpoint_pattern = f"requests:endpoint:*:{date_key}"
                for key in self.redis.scan_iter(endpoint_pattern):
                    endpoint = key.decode().split(":")[2]
                    count = int(self.redis.get(key) or 0)
                    stats["requests_by_endpoint"][endpoint] = stats["requests_by_endpoint"].get(endpoint, 0) + count

                # Requests by status
                status_pattern = f"requests:status:*:{date_key}"
                for key in self.redis.scan_iter(status_pattern):
                    status = key.decode().split(":")[2]
                    count = int(self.redis.get(key) or 0)
                    stats["requests_by_status"][status] = stats["requests_by_status"].get(status, 0) + count

                # Response times
                rt_key = f"response_time:*:{date_key}"
                for key in self.redis.scan_iter(rt_key):
                    times = self.redis.lrange(key, 0, -1)
                    for time_str in times:
                        total_response_time += float(time_str)
                        response_time_count += 1

                current_date += timedelta(days=1)

            # Calculate averages
            if response_time_count > 0:
                stats["average_response_time"] = total_response_time / response_time_count

            stats["total_requests"] = total_requests

            # Get top endpoints
            sorted_endpoints = sorted(
                stats["requests_by_endpoint"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            stats["top_endpoints"] = [{"endpoint": k, "requests": v} for k, v in sorted_endpoints]

            return stats

        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return {"error": str(e)}

    def get_popular_domains(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get most popular domains being analyzed

        Args:
            days: Number of days to look back

        Returns:
            List of popular domains with request counts
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            domain_counts: Dict[str, float] = defaultdict(float)
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                key = f"analyzed_domains:{date_key}"
                # Read top 50 for the day
                for member, score in self.redis.zrange(key, 0, 49, withscores=True):
                    domain = member.decode("utf-8")
                    domain_counts[domain] += float(score)
                current_date += timedelta(days=1)

            top = sorted(domain_counts.items(), key=lambda kv: kv[1], reverse=True)[:20]
            return [{"domain": d, "requests": int(c)} for d, c in top]

        except Exception as e:
            logger.error(f"Error getting popular domains: {str(e)}")
            return []

    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get performance metrics

        Args:
            days: Number of days to look back

        Returns:
            Performance metrics dictionary
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            response_times: List[float] = []
            total_requests = 0
            total_errors = 0

            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                total_requests += int(self.redis.get(f"requests:total:{date_key}") or 0)

                # Count errors as 4xx+5xx
                for key in self.redis.scan_iter(f"requests:status:*:{date_key}"):
                    status = int(key.decode().split(":")[2])
                    count = int(self.redis.get(key) or 0)
                    if status >= 400:
                        total_errors += count

                for key in self.redis.scan_iter(f"response_time:*:{date_key}"):
                    for time_str in self.redis.lrange(key, 0, -1):
                        try:
                            response_times.append(float(time_str))
                        except Exception:
                            continue

                current_date += timedelta(days=1)

            response_times.sort()
            avg = (sum(response_times) / len(response_times)) if response_times else 0.0
            p95 = _percentile(response_times, 0.95)
            p99 = _percentile(response_times, 0.99)

            error_rate = (total_errors / total_requests * 100.0) if total_requests else 0.0
            rps = (total_requests / (days * 24 * 60 * 60)) if days > 0 else 0.0

            return {
                "average_response_time_ms": avg,
                "95th_percentile_response_time_ms": p95,
                "99th_percentile_response_time_ms": p99,
                "error_rate_percent": error_rate,
                "requests_per_second": rps,
            }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {"error": str(e)}

    def _increment_counter(self, key: str):
        """Increment a Redis counter"""
        self.redis.incr(key)

    def _add_to_histogram(self, key: str, value: float, max_samples: int = 1000):
        """Add value to a histogram (using Redis list for simplicity)"""
        # In production, you'd use a proper histogram data structure
        self.redis.lpush(key, str(value))
        self.redis.ltrim(key, 0, max_samples - 1)

    def _track_top_items(self, key: str, item: str, max_items: int = 10):
        """Track top items using Redis sorted set"""
        self.redis.zincrby(key, 1, item)
        # Keep only top items
        self.redis.zremrangebyrank(key, 0, -(max_items + 1))

    def _expire_old_data(self, date_key: str, retention_days: int = 30):
        """Set expiration on old data keys"""
        expire_time = retention_days * 24 * 60 * 60  # 30 days in seconds
        pattern = f"*{date_key}*"
        for key in self.redis.scan_iter(pattern):
            self.redis.expire(key, expire_time)


# Global analytics service instance
analytics_service = AnalyticsService()


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    if p <= 0:
        return float(sorted_values[0])
    if p >= 1:
        return float(sorted_values[-1])
    k = (len(sorted_values) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return float(sorted_values[f])
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return float(d0 + d1)