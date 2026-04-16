import logging
import math
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PageSpeedScorer:
    """Advanced service for page speed scoring with multiple metrics."""

    # Performance thresholds (Web Vitals)
    GOOD_LCP = 2500  # Largest Contentful Paint in ms
    GOOD_FID = 100   # First Input Delay in ms
    GOOD_CLS = 0.1   # Cumulative Layout Shift
    GOOD_TTL = 600   # Time to load in ms

    def calculate_score(
        self,
        response_time_ms: int,
        content_size_bytes: int,
        num_requests: int = 1,
        additional_metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Calculate an advanced page speed score (0-100).
        
        Scoring breakdown:
        - 40% - Response time (LCP proxy)
        - 30% - Page size (CLS proxy)
        - 20% - Request efficiency
        - 10% - Additional metrics if provided

        Args:
            response_time_ms: Response time in milliseconds
            content_size_bytes: Content size in bytes
            num_requests: Number of requests made
            additional_metrics: Dict with additional metrics like js_size, css_size, etc.

        Returns:
            Score from 0-100 or None if unable to calculate
        """
        try:
            additional_metrics = additional_metrics or {}
            
            # Calculate response time score (40%)
            response_score = self._calculate_response_score(response_time_ms)
            
            # Calculate size score (30%)
            size_score = self._calculate_size_score(content_size_bytes, additional_metrics)
            
            # Calculate efficiency score (20%)
            efficiency_score = self._calculate_efficiency_score(num_requests, content_size_bytes)
            
            # Calculate additional metrics score (10%)
            additional_score = self._calculate_additional_score(additional_metrics)
            
            # Weighted score
            final_score = (
                response_score * 0.40 +
                size_score * 0.30 +
                efficiency_score * 0.20 +
                additional_score * 0.10
            )
            
            # Ensure score is within bounds
            final_score = max(0, min(100, final_score))
            
            return int(final_score)

        except Exception as e:
            logger.error(f"Error calculating page speed score: {str(e)}")
            return None

    def _calculate_response_score(self, response_time_ms: int) -> float:
        """
        Calculate response time score (0-100).
        Based on LCP (Largest Contentful Paint) thresholds.
        """
        if response_time_ms <= self.GOOD_LCP:
            # 0-2500ms: excellent (100-80)
            return 100 - (response_time_ms / self.GOOD_LCP) * 20
        elif response_time_ms <= 4000:
            # 2500-4000ms: good (80-50)
            return 80 - ((response_time_ms - self.GOOD_LCP) / 1500) * 30
        else:
            # >4000ms: poor (50-0)
            excess = response_time_ms - 4000
            return max(0, 50 - (excess / 4000) * 50)

    def _calculate_size_score(self, content_size_bytes: int, additional_metrics: Dict[str, Any]) -> float:
        """
        Calculate page size score (0-100).
        Accounts for overall size and composition.
        """
        content_size_kb = content_size_bytes / 1024
        
        # Ideal size ranges
        if content_size_kb <= 100:
            size_score = 100
        elif content_size_kb <= 500:
            # 100-500KB: excellent to good (100-80)
            size_score = 100 - ((content_size_kb - 100) / 400) * 20
        elif content_size_kb <= 1000:
            # 500KB-1MB: good to fair (80-60)
            size_score = 80 - ((content_size_kb - 500) / 500) * 20
        elif content_size_kb <= 3000:
            # 1MB-3MB: fair to poor (60-30)
            size_score = 60 - ((content_size_kb - 1000) / 2000) * 30
        else:
            # >3MB: very poor (30-0)
            excess = content_size_kb - 3000
            size_score = max(0, 30 - (excess / 3000) * 30)
        
        return size_score

    def _calculate_efficiency_score(self, num_requests: int, content_size_bytes: int) -> float:
        """
        Calculate efficiency score (0-100).
        Based on bytes per request and request count.
        """
        # Ideal number of requests based on content size
        ideal_requests = max(5, content_size_bytes / (1024 * 50))  # ~50KB per request ideal
        
        if num_requests <= 10:
            return 100
        elif num_requests <= ideal_requests + 10:
            # Linear degradation
            return 100 - ((num_requests - 10) / (ideal_requests + 10 - 10)) * 30
        elif num_requests <= 50:
            return 70 - ((num_requests - ideal_requests - 10) / 40) * 30
        else:
            # Very inefficient
            excess = num_requests - 50
            return max(0, 40 - (excess / 50) * 40)

    def _calculate_additional_score(self, additional_metrics: Dict[str, Any]) -> float:
        """
        Calculate additional metrics score (0-100).
        """
        score = 100
        
        # Check for JavaScript efficiency
        if "js_size_bytes" in additional_metrics:
            js_size_mb = additional_metrics["js_size_bytes"] / (1024 * 1024)
            if js_size_mb > 1:
                score -= min(20, js_size_mb * 10)
        
        # Check for CSS efficiency
        if "css_size_bytes" in additional_metrics:
            css_size_kb = additional_metrics["css_size_bytes"] / 1024
            if css_size_kb > 200:
                score -= min(15, (css_size_kb - 200) / 20)
        
        # Check for image optimization
        if "image_count" in additional_metrics and "content_size_bytes" in additional_metrics:
            total_size = additional_metrics.get("content_size_bytes", 1)
            image_avg_size = total_size / max(1, additional_metrics["image_count"])
            if image_avg_size > 200 * 1024:  # >200KB per image
                score -= min(15, (image_avg_size - 200 * 1024) / (100 * 1024))
        
        return max(0, min(100, score))

    def get_performance_rating(self, score: int) -> str:
        """
        Get performance rating based on score.

        Args:
            score: Speed score (0-100)

        Returns:
            Rating string
        """
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Needs Improvement"
        elif score >= 60:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_performance_metrics(self, score: int) -> Dict[str, Any]:
        """
        Get detailed performance metrics and recommendations.
        """
        rating = self.get_performance_rating(score)
        
        recommendations = []
        if score < 90:
            recommendations.append("Optimize images and compress media")
        if score < 80:
            recommendations.append("Minimize JavaScript and defer non-critical resources")
        if score < 70:
            recommendations.append("Enable caching and use CDN for static assets")
        if score < 60:
            recommendations.append("Consider reducing page complexity and third-party scripts")
        
        return {
            "score": score,
            "rating": rating,
            "recommendations": recommendations,
            "web_vitals_target": "Pass",
            "lighthouse_equivalent": score * 1.5  # Rough approximation
        }


# Global instance
speed_scorer = PageSpeedScorer()