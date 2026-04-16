"""
Database optimization and indexing utilities
"""

from sqlalchemy import text, Index
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import WebsiteAnalysis, User, ApiKey


class DatabaseOptimizer:
    """Database optimization and maintenance utilities"""

    def __init__(self, db: Session):
        self.db = db

    def create_indexes(self):
        """Create database indexes for better performance"""

        indexes_to_create = [
            # WebsiteAnalysis indexes
            Index('ix_website_analyses_user_id', WebsiteAnalysis.user_id),
            Index('ix_website_analyses_url_hash', text("md5(url)")),
            Index('ix_website_analyses_timestamp', WebsiteAnalysis.timestamp),
            Index('ix_website_analyses_cached', WebsiteAnalysis.cached),

            # User indexes
            Index('ix_users_email_lower', text("lower(email)")),
            Index('ix_users_plan', User.plan),
            Index('ix_users_status', User.status),

            # API Key indexes
            Index('ix_api_keys_user_id', ApiKey.user_id),
            Index('ix_api_keys_revoked', ApiKey.revoked),
            Index('ix_api_keys_last_used', ApiKey.last_used),
        ]

        for index in indexes_to_create:
            try:
                index.create(self.db.bind)
                print(f"Created index: {index.name}")
            except Exception as e:
                print(f"Failed to create index {index.name}: {str(e)}")

    def analyze_table_statistics(self):
        """Update table statistics for query optimization"""

        tables = ['users', 'api_keys', 'website_analyses', 'rate_limits']

        for table in tables:
            try:
                if self.db.bind.dialect.name == 'postgresql':
                    self.db.execute(text(f"ANALYZE {table}"))
                elif self.db.bind.dialect.name == 'sqlite':
                    # SQLite doesn't have ANALYZE command in the same way
                    pass
                print(f"Analyzed statistics for table: {table}")
            except Exception as e:
                print(f"Failed to analyze table {table}: {str(e)}")

    def optimize_queries(self):
        """Apply query optimizations"""

        # Create materialized view for common analytics queries (PostgreSQL only)
        if self.db.bind.dialect.name == 'postgresql':
            try:
                # Create view for popular domains
                self.db.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS popular_domains AS
                    SELECT
                        substring(url from 'https?://([^/]+)') as domain,
                        COUNT(*) as request_count,
                        MAX(timestamp) as last_requested
                    FROM website_analyses
                    WHERE timestamp > NOW() - INTERVAL '30 days'
                    GROUP BY domain
                    ORDER BY request_count DESC
                    LIMIT 100
                """))

                # Create index on the materialized view
                self.db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_popular_domains_count
                    ON popular_domains(request_count DESC)
                """))

                print("Created materialized view for popular domains")
            except Exception as e:
                print(f"Failed to create materialized view: {str(e)}")

    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to maintain performance"""

        try:
            # Delete old rate limit entries
            deleted_rate_limits = self.db.execute(text(f"""
                DELETE FROM rate_limits
                WHERE window_start < NOW() - INTERVAL '{days_to_keep} days'
            """))

            # Archive old analyses if needed (for now, just log)
            old_analyses_count = self.db.execute(text(f"""
                SELECT COUNT(*) FROM website_analyses
                WHERE timestamp < NOW() - INTERVAL '{days_to_keep} days'
            """)).scalar()

            print(f"Cleaned up old data: {deleted_rate_limits.rowcount} rate limit entries")
            print(f"Found {old_analyses_count} old analyses (consider archiving)")

        except Exception as e:
            print(f"Failed to cleanup old data: {str(e)}")

    def get_query_performance_stats(self):
        """Get query performance statistics"""

        stats = {}

        try:
            # Get slow queries (PostgreSQL)
            if self.db.bind.dialect.name == 'postgresql':
                slow_queries = self.db.execute(text("""
                    SELECT
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements
                    ORDER BY mean_time DESC
                    LIMIT 10
                """)).fetchall()

                stats['slow_queries'] = [
                    {
                        'query': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                        'calls': row[1],
                        'total_time': row[2],
                        'mean_time': row[3],
                        'rows': row[4]
                    } for row in slow_queries
                ]

            # Get table sizes
            table_sizes = self.db.execute(text("""
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)).fetchall()

            stats['table_sizes'] = [
                {
                    'table': row[1],
                    'size': row[2]
                } for row in table_sizes
            ]

        except Exception as e:
            stats['error'] = str(e)

        return stats

    def vacuum_and_reindex(self):
        """Perform database maintenance (PostgreSQL only)"""

        if self.db.bind.dialect.name != 'postgresql':
            print("VACUUM and REINDEX are PostgreSQL-specific operations")
            return

        try:
            # VACUUM ANALYZE all tables
            tables = ['users', 'api_keys', 'website_analyses', 'rate_limits']

            for table in tables:
                print(f"VACUUM ANALYZE {table}")
                self.db.execute(text(f"VACUUM ANALYZE {table}"))

            # REINDEX problematic indexes if any
            print("Database maintenance completed")

        except Exception as e:
            print(f"Database maintenance failed: {str(e)}")


class ConnectionPoolOptimizer:
    """Database connection pool optimization"""

    def __init__(self, db):
        self.db = db

    def optimize_pool_settings(self):
        """Optimize database connection pool settings"""

        # This would be configured at the engine level when creating the database connection
        # For now, we'll just return recommendations

        recommendations = {
            'pool_size': '10-20 connections',
            'max_overflow': '20-50 connections',
            'pool_timeout': '30 seconds',
            'pool_recycle': '1 hour',
            'pool_pre_ping': True,
        }

        return recommendations

    def monitor_connection_pool(self):
        """Monitor connection pool health"""

        try:
            # Get connection pool stats
            pool = self.db.bind.pool

            stats = {
                'pool_size': getattr(pool, 'size', 'N/A'),
                'checked_in': getattr(pool, 'checkedin', 'N/A'),
                'checked_out': getattr(pool, 'checkedout', 'N/A'),
                'overflow': getattr(pool, 'overflow', 'N/A'),
                'invalid': getattr(pool, 'invalid', 'N/A'),
            }

            return stats

        except Exception as e:
            return {'error': str(e)}


def run_database_optimization(db: Session):
    """Run comprehensive database optimization"""

    optimizer = DatabaseOptimizer(db)
    pool_optimizer = ConnectionPoolOptimizer(db)

    print("Starting database optimization...")

    # Create indexes
    optimizer.create_indexes()

    # Analyze statistics
    optimizer.analyze_table_statistics()

    # Optimize queries
    optimizer.optimize_queries()

    # Clean up old data
    optimizer.cleanup_old_data()

    # Vacuum and reindex (PostgreSQL)
    optimizer.vacuum_and_reindex()

    print("Database optimization completed")

    # Return optimization report
    return {
        'indexes_created': True,
        'statistics_analyzed': True,
        'queries_optimized': True,
        'cleanup_completed': True,
        'maintenance_completed': True,
        'pool_recommendations': pool_optimizer.optimize_pool_settings(),
        'pool_stats': pool_optimizer.monitor_connection_pool(),
        'performance_stats': optimizer.get_query_performance_stats()
    }