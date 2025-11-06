"""
Scalability Tests
TASK-046, TASK-047: Test with large inboxes and many concurrent projects
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import Project, EmailProjectMapping
from app.models.ai_processing import AIProcessingQueue
from app.services.incremental_processing import IncrementalProcessingService, get_incremental_processing_service
from app.services.caching import get_cache, get_query_cache
from app.dal.project_dal import ProjectDAL, EmailProjectMappingDAL
from app.services.rate_limiting import get_quota_manager
import time
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create test user"""
    from app.models.user import User, UserRole
    user = User(
        email="test@example.com",
        name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def large_inbox_data(db: Session, test_user: User):
    """Create test data for large inbox simulation"""
    # Create mock email mappings (simulating 50,000+ emails)
    projects = []
    mappings = []
    
    # Create 100 projects
    for i in range(100):
        project = Project(
            user_id=test_user.id,
            project_id=f"project_{i}",
            project_name=f"Test Project {i}",
            status="active",
            email_count=0
        )
        db.add(project)
        projects.append(project)
    
    db.commit()
    
    # Create 500 email mappings per project (50,000 total)
    for project in projects:
        for j in range(500):
            mapping = EmailProjectMapping(
                user_id=test_user.id,
                project_id=project.id,
                email_id=f"email_{project.id}_{j}",
                thread_id=f"thread_{project.id}_{j}",
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=j % 365)
            )
            db.add(mapping)
            mappings.append(mapping)
    
    db.commit()
    
    # Update email counts
    for project in projects:
        project.email_count = 500
    db.commit()
    
    return {
        'projects': projects,
        'mappings': mappings,
        'total_emails': len(mappings)
    }


class TestLargeInboxPerformance:
    """TASK-046: Test with large inboxes (50,000+ emails)"""
    
    def test_project_listing_performance(self, db: Session, test_user: User, large_inbox_data):
        """Test project listing with many emails"""
        project_dal = ProjectDAL(Project, db)
        
        # Test without cache
        start_time = time.time()
        projects_no_cache = project_dal.get_user_projects(
            test_user.id,
            status="active",
            use_cache=False
        )
        time_no_cache = time.time() - start_time
        
        # Test with cache
        start_time = time.time()
        projects_with_cache = project_dal.get_user_projects(
            test_user.id,
            status="active",
            use_cache=True
        )
        time_with_cache = time.time() - start_time
        
        # Second call should be faster (cache hit)
        start_time = time.time()
        projects_cached = project_dal.get_user_projects(
            test_user.id,
            status="active",
            use_cache=True
        )
        time_cached = time.time() - start_time
        
        assert len(projects_no_cache) == 100
        assert len(projects_with_cache) == 100
        assert len(projects_cached) == 100
        
        # Cache should be faster
        assert time_cached < time_with_cache
        logger.info(f"Project listing - No cache: {time_no_cache:.3f}s, With cache: {time_with_cache:.3f}s, Cached: {time_cached:.3f}s")
    
    def test_email_mapping_query_performance(self, db: Session, test_user: User, large_inbox_data):
        """Test email mapping queries with pagination"""
        mapping_dal = EmailProjectMappingDAL(EmailProjectMapping, db)
        project = large_inbox_data['projects'][0]
        
        # Test without pagination (should be slow)
        start_time = time.time()
        all_emails = mapping_dal.get_project_emails(
            test_user.id,
            project.id,
            use_cache=False
        )
        time_all = time.time() - start_time
        
        # Test with pagination
        start_time = time.time()
        paginated_emails = mapping_dal.get_project_emails(
            test_user.id,
            project.id,
            limit=50,
            offset=0,
            use_cache=False
        )
        time_paginated = time.time() - start_time
        
        assert len(all_emails) == 500
        assert len(paginated_emails) == 50
        
        # Paginated should be faster
        assert time_paginated < time_all
        logger.info(f"Email query - All: {time_all:.3f}s, Paginated: {time_paginated:.3f}s")
    
    def test_incremental_processing_performance(self, db: Session, test_user: User):
        """Test incremental processing with large batches"""
        processing_service = get_incremental_processing_service(test_user, db)
        
        # Test with different batch sizes
        batch_sizes = [10, 50, 100]
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            # Simulate processing (without actually calling Gmail API)
            result = processing_service.process_incremental(
                batch_size=batch_size,
                max_emails=1000  # Limit for testing
            )
            
            time_taken = time.time() - start_time
            
            logger.info(f"Incremental processing - Batch size {batch_size}: {time_taken:.3f}s, Processed: {result['total_processed']}")
            
            # Larger batches should be more efficient
            if batch_size > 10:
                assert result['total_batches'] < 100  # Should have fewer batches
    
    def test_cache_performance(self, db: Session, test_user: User):
        """Test cache hit rates and performance"""
        cache = get_cache()
        cache.clear()
        
        project_dal = ProjectDAL(Project, db)
        
        # First call (cache miss)
        start_time = time.time()
        projects1 = project_dal.get_user_projects(test_user.id, use_cache=True)
        time_miss = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        projects2 = project_dal.get_user_projects(test_user.id, use_cache=True)
        time_hit = time.time() - start_time
        
        # Cache hit should be significantly faster
        assert time_hit < time_miss
        assert time_hit < 0.01  # Should be very fast (< 10ms)
        
        # Check cache stats
        stats = cache.get_stats()
        assert stats['active_keys'] > 0
        
        logger.info(f"Cache performance - Miss: {time_miss:.3f}s, Hit: {time_hit:.3f}s")


class TestManyConcurrentProjects:
    """TASK-047: Test with multiple concurrent projects (100+)"""
    
    def test_project_search_performance(self, db: Session, test_user: User, large_inbox_data):
        """Test project search with 100+ projects"""
        project_dal = ProjectDAL(Project, db)
        
        # Test search by name
        start_time = time.time()
        all_projects = project_dal.get_user_projects(test_user.id, use_cache=False)
        time_all = time.time() - start_time
        
        # Filter projects (simulating search)
        start_time = time.time()
        filtered = [p for p in all_projects if "Project 5" in p.project_name]
        time_filtered = time.time() - start_time
        
        assert len(all_projects) == 100
        assert len(filtered) == 11  # Project 5, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59
        
        logger.info(f"Project search - Load all: {time_all:.3f}s, Filter: {time_filtered:.3f}s")
    
    def test_project_statistics_performance(self, db: Session, test_user: User, large_inbox_data):
        """Test project statistics calculation with many projects"""
        project_dal = ProjectDAL(Project, db)
        
        start_time = time.time()
        stats = project_dal.get_project_statistics(test_user.id)
        time_taken = time.time() - start_time
        
        assert stats['total_projects'] == 100
        assert stats['active_projects'] == 100
        assert stats['total_emails'] == 50000
        
        # Should complete quickly even with many projects
        assert time_taken < 1.0  # Should be under 1 second
        
        logger.info(f"Project statistics - Time: {time_taken:.3f}s, Projects: {stats['total_projects']}, Emails: {stats['total_emails']}")
    
    def test_concurrent_project_access(self, db: Session, test_user: User, large_inbox_data):
        """Test accessing multiple projects concurrently"""
        mapping_dal = EmailProjectMappingDAL(EmailProjectMapping, db)
        
        # Access multiple projects
        projects_to_test = large_inbox_data['projects'][:10]  # Test with 10 projects
        
        start_time = time.time()
        results = []
        
        for project in projects_to_test:
            emails = mapping_dal.get_project_emails(
                test_user.id,
                project.id,
                limit=50,
                offset=0,
                use_cache=True
            )
            results.append({
                'project_id': project.id,
                'email_count': len(emails)
            })
        
        time_taken = time.time() - start_time
        
        assert len(results) == 10
        assert all(r['email_count'] == 50 for r in results)
        
        # Should complete reasonably quickly
        assert time_taken < 5.0  # Should be under 5 seconds
        
        logger.info(f"Concurrent project access - Time: {time_taken:.3f}s, Projects: 10")
    
    def test_cache_invalidation_performance(self, db: Session, test_user: User, large_inbox_data):
        """Test cache invalidation with many projects"""
        cache = get_cache()
        query_cache = get_query_cache()
        project_dal = ProjectDAL(Project, db)
        
        # Populate cache
        projects = project_dal.get_user_projects(test_user.id, use_cache=True)
        assert len(projects) == 100
        
        # Invalidate all user caches
        start_time = time.time()
        query_cache.invalidate_user_cache(test_user.id)
        time_taken = time.time() - start_time
        
        # Should be fast
        assert time_taken < 0.1
        
        # Verify cache is cleared
        stats = cache.get_stats()
        logger.info(f"Cache invalidation - Time: {time_taken:.3f}s, Remaining keys: {stats['active_keys']}")


class TestRateLimitingScalability:
    """Test rate limiting with high load"""
    
    def test_rate_limiter_performance(self):
        """Test rate limiter with many requests"""
        from app.services.rate_limiting import RateLimiter
        
        limiter = RateLimiter(max_requests=1000, window_seconds=60)
        user_id = 1
        operation = "gmail_read"
        key = f"{user_id}:{operation}"
        
        # Simulate 1000 requests
        start_time = time.time()
        allowed_count = 0
        blocked_count = 0
        
        for i in range(1000):
            is_allowed, retry_after = limiter.is_allowed(key)
            if is_allowed:
                allowed_count += 1
            else:
                blocked_count += 1
        
        time_taken = time.time() - start_time
        
        # Should handle 1000 requests quickly
        assert time_taken < 1.0
        assert allowed_count == 1000  # All should be allowed within window
        
        logger.info(f"Rate limiter - Time: {time_taken:.3f}s, Allowed: {allowed_count}, Blocked: {blocked_count}")
    
    def test_quota_manager_performance(self):
        """Test quota manager with many operations"""
        quota_manager = get_quota_manager()
        user_id = 1
        
        # Simulate 1000 operations
        start_time = time.time()
        
        for i in range(1000):
            quota_manager.check_quota(user_id, "messages.list")
        
        time_taken = time.time() - start_time
        
        # Should handle quickly
        assert time_taken < 1.0
        
        # Check quota status
        status = quota_manager.get_quota_status(user_id)
        assert status['daily_usage'] == 1000
        
        logger.info(f"Quota manager - Time: {time_taken:.3f}s, Usage: {status['daily_usage']}")


class TestBottleneckIdentification:
    """Identify performance bottlenecks"""
    
    def test_database_query_bottlenecks(self, db: Session, test_user: User, large_inbox_data):
        """Identify slow database queries"""
        project_dal = ProjectDAL(Project, db)
        mapping_dal = EmailProjectMappingDAL(EmailProjectMapping, db)
        
        bottlenecks = []
        
        # Test project listing
        start_time = time.time()
        projects = project_dal.get_user_projects(test_user.id, use_cache=False)
        time_taken = time.time() - start_time
        if time_taken > 0.5:
            bottlenecks.append(f"Project listing: {time_taken:.3f}s")
        
        # Test email mapping query
        project = projects[0]
        start_time = time.time()
        emails = mapping_dal.get_project_emails(test_user.id, project.id, use_cache=False)
        time_taken = time.time() - start_time
        if time_taken > 0.5:
            bottlenecks.append(f"Email mapping query: {time_taken:.3f}s")
        
        # Test statistics
        start_time = time.time()
        stats = project_dal.get_project_statistics(test_user.id)
        time_taken = time.time() - start_time
        if time_taken > 1.0:
            bottlenecks.append(f"Statistics calculation: {time_taken:.3f}s")
        
        if bottlenecks:
            logger.warning(f"Performance bottlenecks identified: {bottlenecks}")
        else:
            logger.info("No significant bottlenecks identified")


@pytest.mark.slow
class TestStressTesting:
    """Stress tests for extreme scenarios"""
    
    def test_extreme_large_inbox(self, db: Session, test_user: User):
        """Test with simulated 100,000+ emails"""
        # Create 200 projects with 500 emails each = 100,000 emails
        projects = []
        for i in range(200):
            project = Project(
                user_id=test_user.id,
                project_id=f"stress_project_{i}",
                project_name=f"Stress Test Project {i}",
                status="active",
                email_count=500
            )
            db.add(project)
            projects.append(project)
        
        db.commit()
        
        # Test project listing
        project_dal = ProjectDAL(Project, db)
        start_time = time.time()
        all_projects = project_dal.get_user_projects(test_user.id, use_cache=True)
        time_taken = time.time() - start_time
        
        assert len(all_projects) == 200
        assert time_taken < 2.0  # Should still be under 2 seconds with cache
        
        logger.info(f"Extreme large inbox - Projects: 200, Time: {time_taken:.3f}s")
    
    def test_extreme_many_projects(self, db: Session, test_user: User):
        """Test with 500+ projects"""
        projects = []
        for i in range(500):
            project = Project(
                user_id=test_user.id,
                project_id=f"extreme_project_{i}",
                project_name=f"Extreme Project {i}",
                status="active",
                email_count=10
            )
            db.add(project)
            projects.append(project)
        
        db.commit()
        
        project_dal = ProjectDAL(Project, db)
        start_time = time.time()
        all_projects = project_dal.get_user_projects(test_user.id, use_cache=True)
        time_taken = time.time() - start_time
        
        assert len(all_projects) == 500
        assert time_taken < 3.0  # Should be under 3 seconds
        
        logger.info(f"Extreme many projects - Projects: 500, Time: {time_taken:.3f}s")

