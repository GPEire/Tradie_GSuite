"""
Performance Benchmarks
TASK-046, TASK-047: Performance benchmarks for scalability testing
"""

import pytest
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import Project, EmailProjectMapping
from app.dal.project_dal import ProjectDAL, EmailProjectMappingDAL
from app.services.caching import get_cache
from app.services.incremental_processing import get_incremental_processing_service
import logging

logger = logging.getLogger(__name__)


class PerformanceBenchmarks:
    """Performance benchmarks for scalability"""
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.results = []
    
    def benchmark_project_listing(self, num_projects: int, use_cache: bool = True):
        """Benchmark project listing performance"""
        project_dal = ProjectDAL(Project, self.db)
        
        # Create test projects
        projects = []
        for i in range(num_projects):
            project = Project(
                user_id=self.user.id,
                project_id=f"bench_project_{i}",
                project_name=f"Benchmark Project {i}",
                status="active",
                email_count=100
            )
            self.db.add(project)
            projects.append(project)
        
        self.db.commit()
        
        # Clear cache
        if not use_cache:
            get_cache().clear()
        
        # Benchmark
        start_time = time.time()
        result = project_dal.get_user_projects(self.user.id, use_cache=use_cache)
        time_taken = time.time() - start_time
        
        self.results.append({
            'test': 'project_listing',
            'num_projects': num_projects,
            'use_cache': use_cache,
            'time_taken': time_taken,
            'items_per_second': num_projects / time_taken if time_taken > 0 else 0
        })
        
        # Cleanup
        for project in projects:
            self.db.delete(project)
        self.db.commit()
        
        return time_taken
    
    def benchmark_email_query(self, num_emails: int, use_pagination: bool = True):
        """Benchmark email query performance"""
        # Create project with emails
        project = Project(
            user_id=self.user.id,
            project_id="bench_email_project",
            project_name="Benchmark Email Project",
            status="active",
            email_count=num_emails
        )
        self.db.add(project)
        self.db.commit()
        
        mapping_dal = EmailProjectMappingDAL(EmailProjectMapping, self.db)
        
        # Create email mappings
        mappings = []
        for i in range(num_emails):
            mapping = EmailProjectMapping(
                user_id=self.user.id,
                project_id=project.id,
                email_id=f"bench_email_{i}",
                is_active=True
            )
            self.db.add(mapping)
            mappings.append(mapping)
        
        self.db.commit()
        
        # Benchmark
        start_time = time.time()
        
        if use_pagination:
            result = mapping_dal.get_project_emails(
                self.user.id,
                project.id,
                limit=50,
                offset=0,
                use_cache=False
            )
        else:
            result = mapping_dal.get_project_emails(
                self.user.id,
                project.id,
                use_cache=False
            )
        
        time_taken = time.time() - start_time
        
        self.results.append({
            'test': 'email_query',
            'num_emails': num_emails,
            'use_pagination': use_pagination,
            'time_taken': time_taken,
            'items_returned': len(result)
        })
        
        # Cleanup
        for mapping in mappings:
            self.db.delete(mapping)
        self.db.delete(project)
        self.db.commit()
        
        return time_taken
    
    def benchmark_cache_performance(self, num_operations: int):
        """Benchmark cache performance"""
        cache = get_cache()
        cache.clear()
        
        project_dal = ProjectDAL(Project, self.db)
        
        # Create test project
        project = Project(
            user_id=self.user.id,
            project_id="bench_cache_project",
            project_name="Benchmark Cache Project",
            status="active"
        )
        self.db.add(project)
        self.db.commit()
        
        # Benchmark cache misses
        start_time = time.time()
        for i in range(num_operations):
            _ = project_dal.get_user_projects(self.user.id, use_cache=True)
        time_with_cache = time.time() - start_time
        
        # Clear cache
        cache.clear()
        
        # Benchmark without cache
        start_time = time.time()
        for i in range(num_operations):
            _ = project_dal.get_user_projects(self.user.id, use_cache=False)
        time_without_cache = time.time() - start_time
        
        cache_improvement = ((time_without_cache - time_with_cache) / time_without_cache) * 100
        
        self.results.append({
            'test': 'cache_performance',
            'num_operations': num_operations,
            'time_with_cache': time_with_cache,
            'time_without_cache': time_without_cache,
            'cache_improvement_percent': cache_improvement
        })
        
        # Cleanup
        self.db.delete(project)
        self.db.commit()
        
        return cache_improvement
    
    def generate_report(self) -> dict:
        """Generate performance report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'results': self.results,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> dict:
        """Generate summary statistics"""
        project_listing_tests = [r for r in self.results if r['test'] == 'project_listing']
        email_query_tests = [r for r in self.results if r['test'] == 'email_query']
        cache_tests = [r for r in self.results if r['test'] == 'cache_performance']
        
        summary = {}
        
        if project_listing_tests:
            cached_tests = [r for r in project_listing_tests if r['use_cache']]
            if cached_tests:
                summary['avg_project_listing_time_cached'] = sum(r['time_taken'] for r in cached_tests) / len(cached_tests)
        
        if email_query_tests:
            paginated_tests = [r for r in email_query_tests if r['use_pagination']]
            if paginated_tests:
                summary['avg_email_query_time_paginated'] = sum(r['time_taken'] for r in paginated_tests) / len(paginated_tests)
        
        if cache_tests:
            summary['avg_cache_improvement'] = sum(r['cache_improvement_percent'] for r in cache_tests) / len(cache_tests)
        
        return summary


@pytest.fixture
def benchmark_instance(db: Session, test_user: User) -> PerformanceBenchmarks:
    """Create benchmark instance"""
    return PerformanceBenchmarks(db, test_user)


def test_scalability_benchmarks(benchmark_instance: PerformanceBenchmarks):
    """Run scalability benchmarks"""
    # Test with different project counts
    for num_projects in [10, 50, 100, 200]:
        time_taken = benchmark_instance.benchmark_project_listing(num_projects, use_cache=True)
        logger.info(f"Project listing ({num_projects} projects, cached): {time_taken:.3f}s")
    
    # Test with different email counts
    for num_emails in [100, 500, 1000, 5000]:
        time_taken = benchmark_instance.benchmark_email_query(num_emails, use_pagination=True)
        logger.info(f"Email query ({num_emails} emails, paginated): {time_taken:.3f}s")
    
    # Test cache performance
    improvement = benchmark_instance.benchmark_cache_performance(100)
    logger.info(f"Cache improvement: {improvement:.1f}%")
    
    # Generate report
    report = benchmark_instance.generate_report()
    logger.info(f"Performance report: {report['summary']}")

