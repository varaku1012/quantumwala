#!/usr/bin/env python3
"""
Complete test of the Context Engineering System with a real spec workflow
Tests all components: Bridge, Memory, Context, Integration
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from integrated_system import IntegratedSystem
from spec_manager import SpecManager, SpecStage
from context_engine import ContextEngine
from memory_manager import MemoryManager

class WorkflowTester:
    """Complete workflow tester for Context Engineering System"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.results = {}
        self.test_spec_name = "user-auth-test"
        
    async def run_complete_test(self):
        """Run complete test workflow"""
        print("=" * 70)
        print("CONTEXT ENGINEERING SYSTEM - COMPLETE WORKFLOW TEST")
        print("=" * 70)
        print(f"Test Spec: {self.test_spec_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("-" * 70)
        
        # Phase 1: System Initialization
        print("\n[PHASE 1] System Initialization")
        print("-" * 35)
        system = await self.initialize_system()
        if not system:
            return False
            
        # Phase 2: Spec Creation
        print("\n[PHASE 2] Spec Creation")
        print("-" * 35)
        spec_created = await self.create_test_spec()
        if not spec_created:
            print("[ERROR] Failed to create spec")
            return False
            
        # Phase 3: Workflow Execution
        print("\n[PHASE 3] Workflow Execution")
        print("-" * 35)
        workflow_result = await self.execute_workflow(system)
        
        # Phase 4: Memory Verification
        print("\n[PHASE 4] Memory Persistence Verification")
        print("-" * 35)
        memory_verified = await self.verify_memory_persistence(system)
        
        # Phase 5: Context Testing
        print("\n[PHASE 5] Context Compression Testing")
        print("-" * 35)
        context_tested = await self.test_context_compression(system)
        
        # Phase 6: Database Verification
        print("\n[PHASE 6] Database Storage Verification")
        print("-" * 35)
        db_verified = await self.verify_database_storage()
        
        # Final Report
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        self.print_results()
        
        all_passed = all([
            system is not None,
            spec_created,
            workflow_result.get('success', False) if workflow_result else False,
            memory_verified,
            context_tested,
            db_verified
        ])
        
        if all_passed:
            print("\n[SUCCESS] ALL TESTS PASSED!")
            print("The Context Engineering System is fully functional.")
        else:
            print("\n[WARNING] Some tests failed. Check results above.")
            
        return all_passed
    
    async def initialize_system(self):
        """Initialize and validate the integrated system"""
        try:
            print("Initializing IntegratedSystem...")
            system = IntegratedSystem()
            
            # Check health
            health = system.health_check()
            print("\nSystem Health Check:")
            for component, status in health.items():
                status_text = "[PASS]" if status else "[FAIL]"
                print(f"  {status_text} {component}: {status}")
            
            self.results['system_initialization'] = health['system_healthy']
            
            if health['system_healthy']:
                print("\n[SUCCESS] System initialized and healthy")
                return system
            else:
                print("\n[ERROR] System not healthy")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to initialize system: {e}")
            self.results['system_initialization'] = False
            return None
    
    async def create_test_spec(self):
        """Create a test specification"""
        try:
            print(f"Creating spec: {self.test_spec_name}")
            
            spec_mgr = SpecManager()
            
            # Create the spec
            success = spec_mgr.create_spec(
                name=self.test_spec_name,
                description="User authentication system with JWT, MFA, password reset, and session management",
                stage=SpecStage.SCOPE
            )
            
            if success:
                print(f"[SUCCESS] Spec created at: .claude/specs/scope/{self.test_spec_name}")
                
                # Add some content to the spec
                spec_dir = Path(f".claude/specs/scope/{self.test_spec_name}")
                
                # Create requirements file
                requirements = """# User Authentication Requirements

## Functional Requirements
1. User Registration with email verification
2. Secure login with JWT tokens
3. Password reset via email
4. Multi-factor authentication (MFA)
5. Session management
6. Role-based access control (RBAC)

## Technical Requirements
- JWT token expiry: 24 hours
- Password: min 8 chars, special chars required
- MFA: TOTP-based (Google Authenticator compatible)
- Database: PostgreSQL for user data
- Cache: Redis for sessions
"""
                (spec_dir / "requirements.md").write_text(requirements)
                print("  - Created requirements.md")
                
                # Create design file
                design = """# Authentication System Design

## Architecture
- REST API with JWT authentication
- Stateless authentication
- Redis session cache
- PostgreSQL user store

## Endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh
- POST /auth/reset-password
- POST /auth/verify-email
- POST /auth/mfa/enable
- POST /auth/mfa/verify
"""
                (spec_dir / "design.md").write_text(design)
                print("  - Created design.md")
                
                self.results['spec_creation'] = True
                return True
            else:
                print(f"[ERROR] Failed to create spec")
                self.results['spec_creation'] = False
                return False
                
        except Exception as e:
            print(f"[ERROR] Spec creation failed: {e}")
            self.results['spec_creation'] = False
            return False
    
    async def execute_workflow(self, system):
        """Execute a workflow through the integrated system"""
        try:
            print(f"Executing workflow for spec: {self.test_spec_name}")
            
            # Execute workflow
            result = await system.execute_workflow(
                description="Implement complete user authentication system with JWT, MFA, and password reset",
                spec_name=self.test_spec_name
            )
            
            print(f"\nWorkflow Execution Result:")
            print(f"  - Success: {result.get('success', False)}")
            print(f"  - Duration: {result.get('duration', 0):.2f}s")
            
            if result.get('error'):
                print(f"  - Error: {result['error']}")
            
            self.results['workflow_execution'] = result.get('success', False)
            return result
            
        except Exception as e:
            print(f"[ERROR] Workflow execution failed: {e}")
            self.results['workflow_execution'] = False
            return {'success': False, 'error': str(e)}
    
    async def verify_memory_persistence(self, system):
        """Verify that memories are being persisted"""
        try:
            print("Testing memory persistence...")
            
            # Store a test memory
            test_result = {
                'success': True,
                'output': 'Test authentication implementation',
                'duration': 2.5,
                'task_type': 'authentication'
            }
            
            system.memory_manager.store_execution(
                task_id=f"test_auth_{datetime.now().timestamp()}",
                agent='architect',
                result=test_result
            )
            print("  - Stored test memory")
            
            # Retrieve memories
            memories = system.memory_manager.get_relevant_memories({
                'type': 'authentication',
                'agent': 'architect'
            })
            
            print(f"\nMemory Retrieval Results:")
            print(f"  - Short-term memories: {len(memories.get('short_term', {}))}")
            print(f"  - Long-term memories: {len(memories.get('long_term', []))}")
            print(f"  - Episodic examples: {len(memories.get('episodic', []))}")
            
            # Verify at least one memory exists
            has_memories = (
                len(memories.get('short_term', {})) > 0 or
                len(memories.get('long_term', [])) > 0
            )
            
            self.results['memory_persistence'] = has_memories
            
            if has_memories:
                print("\n[SUCCESS] Memory persistence verified")
            else:
                print("\n[WARNING] No memories found")
                
            return has_memories
            
        except Exception as e:
            print(f"[ERROR] Memory verification failed: {e}")
            self.results['memory_persistence'] = False
            return False
    
    async def test_context_compression(self, system):
        """Test context compression with token counting"""
        try:
            print("Testing context compression...")
            
            # Create large context
            large_context = {
                'requirements': "This is a very long requirements document. " * 200,
                'design': "This is a detailed design specification. " * 150,
                'implementation': "Code implementation details. " * 100,
                'current_task': {
                    'id': 'task-auth-1',
                    'description': 'Implement JWT token generation'
                }
            }
            
            print(f"  - Original context size: {sum(len(str(v)) for v in large_context.values())} chars")
            
            # Compress context
            compressed = system.context_engine.prepare_context(
                agent_type='developer',
                task={'description': 'Implement JWT authentication'},
                full_context=large_context
            )
            
            # Count tokens
            token_count = system.context_engine.compressor._count_tokens(compressed)
            print(f"  - Compressed context: {token_count} tokens")
            
            # Verify compression worked
            within_limit = token_count <= 4000
            
            if within_limit:
                print(f"\n[SUCCESS] Context compressed to {token_count} tokens (under 4000 limit)")
            else:
                print(f"\n[WARNING] Context too large: {token_count} tokens (exceeds 4000 limit)")
            
            self.results['context_compression'] = within_limit
            return within_limit
            
        except Exception as e:
            print(f"[ERROR] Context compression test failed: {e}")
            self.results['context_compression'] = False
            return False
    
    async def verify_database_storage(self):
        """Verify database storage and structure"""
        try:
            print("Verifying database storage...")
            
            db_path = Path.cwd() / '.claude' / 'data' / 'memory.db'
            
            if not db_path.exists():
                print("[ERROR] Database file not found")
                self.results['database_storage'] = False
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"\n  Database Tables Found: {len(tables)}")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    - {table}: {count} rows")
            
            # Check for our test data
            cursor.execute("SELECT COUNT(*) FROM memories WHERE agent = 'architect'")
            architect_memories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM health_metrics")
            health_metrics = cursor.fetchone()[0]
            
            conn.close()
            
            # Verify expected tables exist
            expected_tables = ['memories', 'episodic_memories', 'context_cache', 
                             'agent_performance', 'workflows', 'health_metrics']
            tables_exist = all(table in tables for table in expected_tables)
            
            if tables_exist:
                print("\n[SUCCESS] All expected tables exist in database")
            else:
                missing = [t for t in expected_tables if t not in tables]
                print(f"\n[WARNING] Missing tables: {missing}")
            
            self.results['database_storage'] = tables_exist
            return tables_exist
            
        except Exception as e:
            print(f"[ERROR] Database verification failed: {e}")
            self.results['database_storage'] = False
            return False
    
    def print_results(self):
        """Print test results summary"""
        for test_name, passed in self.results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} {test_name.replace('_', ' ').title()}")

async def main():
    """Main test execution"""
    tester = WorkflowTester()
    success = await tester.run_complete_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))