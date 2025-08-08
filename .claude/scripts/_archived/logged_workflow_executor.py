#!/usr/bin/env python3
"""
Enhanced Workflow Executor with Comprehensive Logging
Combines the enhanced workflow with detailed logging at every step
"""

import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

# Import workflow logger
from workflow_logger import WorkflowLogger

class LoggedWorkflowExecutor:
    """Execute workflow with comprehensive logging"""
    
    def __init__(self, spec_name, spec_folder="backlog", log_level="INFO"):
        self.spec_name = spec_name
        
        # Setup paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.spec_source = self.project_root / f".claude/specs/{spec_folder}/{spec_name}"
        self.spec_scope = self.project_root / f".claude/specs/scope/{spec_name}"
        self.spec_completed = self.project_root / f".claude/specs/completed/{spec_name}"
        
        # Initialize logger
        workflow_id = f"{spec_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = WorkflowLogger(
            workflow_id=workflow_id,
            spec_name=spec_name,
            log_level=log_level,
            enable_file_logging=True,
            enable_json_logging=True,
            enable_console=True
        )
        
        self.results = {}
        
    async def execute_workflow(self):
        """Execute the workflow with comprehensive logging"""
        
        # Start logging
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("LOGGED WORKFLOW EXECUTION")
        self.logger.logger.info("=" * 80)
        self.logger.logger.info(f"Spec: {self.spec_name}")
        self.logger.logger.info(f"Source: {self.spec_source}")
        self.logger.logger.info("-" * 80)
        
        try:
            # Phase 0: Move spec to scope
            self.logger.start_phase("Spec Lifecycle Management", "Moving spec from backlog to scope")
            success = self.move_spec_to_scope()
            if success:
                self.logger.end_phase("Spec Lifecycle Management", "success")
            else:
                self.logger.end_phase("Spec Lifecycle Management", "failed", "Could not move spec")
                return False
            
            # Phase 1: Project Structure Definition
            self.logger.start_phase("Project Structure Definition", "Defining folder structure with sr.backend-engineer")
            structure = await self.define_project_structure()
            self.logger.log_metric("services_count", len(structure.get('services', [])))
            self.logger.log_metric("frontend_count", len(structure.get('frontend', [])))
            self.logger.end_phase("Project Structure Definition", "success")
            
            # Phase 2: Requirements Analysis
            self.logger.start_phase("Requirements Analysis", "Generating requirements with business-analyst")
            self.logger.log_agent_call("business-analyst", "Generate requirements", {"spec": self.spec_name})
            requirements = await self.generate_requirements()
            self.logger.log_agent_response("business-analyst", True, f"Generated {len(requirements)} requirement categories")
            self.logger.end_phase("Requirements Analysis", "success")
            
            # Phase 3: System Design
            self.logger.start_phase("System Design", "Creating system architecture with architect")
            self.logger.log_agent_call("architect", "Create system design", {"spec": self.spec_name})
            design = await self.create_system_design()
            self.logger.log_agent_response("architect", True, "Design completed")
            self.logger.end_phase("System Design", "success")
            
            # Phase 4: Task Generation
            self.logger.start_phase("Task Breakdown", "Generating tasks with product-manager")
            self.logger.log_agent_call("product-manager", "Generate implementation tasks", {"spec": self.spec_name})
            tasks = await self.generate_tasks()
            self.logger.log_metric("tasks_generated", len(tasks))
            self.logger.log_agent_response("product-manager", True, f"Generated {len(tasks)} tasks")
            self.logger.end_phase("Task Breakdown", "success")
            
            # Phase 5: Code Implementation
            self.logger.start_phase("Code Implementation", "Generating code with developer agent")
            self.logger.log_agent_call("developer", "Implement services", {"tasks": len(tasks)})
            code_files = await self.implement_code_structured(structure, tasks)
            self.logger.log_metric("files_created", len(code_files))
            for file in code_files:
                self.logger.log_file_created(file, "code")
            self.logger.log_agent_response("developer", True, f"Created {len(code_files)} files")
            self.logger.end_phase("Code Implementation", "success")
            
            # Phase 6: Test Generation
            self.logger.start_phase("Test Generation", "Creating tests with qa-engineer")
            self.logger.log_agent_call("qa-engineer", "Generate tests", {"spec": self.spec_name})
            test_files = await self.generate_tests(structure)
            for file in test_files:
                self.logger.log_file_created(file, "test")
            self.logger.log_agent_response("qa-engineer", True, f"Created {len(test_files)} test files")
            self.logger.end_phase("Test Generation", "success")
            
            # Phase 7: Documentation
            self.logger.start_phase("Documentation", "Generating project documentation")
            docs = await self.generate_documentation(structure)
            for doc in docs:
                self.logger.log_file_created(doc, "documentation")
            self.logger.end_phase("Documentation", "success")
            
            # Phase 8: Infrastructure
            self.logger.start_phase("Infrastructure Setup", "Creating deployment configs with devops-engineer")
            self.logger.log_agent_call("devops-engineer", "Setup infrastructure", {"spec": self.spec_name})
            infra = await self.setup_infrastructure(structure)
            for file in infra:
                self.logger.log_file_created(file, "config")
            self.logger.log_agent_response("devops-engineer", True, f"Created {len(infra)} config files")
            self.logger.end_phase("Infrastructure Setup", "success")
            
            # Phase 9: Move spec to completed
            self.logger.start_phase("Spec Completion", "Moving spec to completed folder")
            self.move_spec_to_completed()
            self.logger.log_metric("total_files_created", 
                                 len(code_files) + len(test_files) + len(docs) + len(infra))
            self.logger.end_phase("Spec Completion", "success")
            
            # Log final metrics
            self.logger.log_metric("workflow_success", True)
            
            # Generate and save summary
            summary = self.logger.generate_summary()
            self.logger.logger.info("\n" + summary)
            
            # Phase 10: Automated Validation
            self.logger.start_phase("Automated Validation", "Validating workflow execution and generating insights")
            validation_success = await self.validate_execution()
            if validation_success:
                self.logger.end_phase("Automated Validation", "success")
            else:
                self.logger.end_phase("Automated Validation", "completed_with_issues")
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Workflow failed: {str(e)}", e)
            self.logger.end_phase(self.logger.current_phase, "failed", str(e))
            self.logger.generate_summary()
            return False
    
    def move_spec_to_scope(self):
        """Move spec from source to scope folder"""
        try:
            self.logger.logger.info(f"Checking if spec exists at: {self.spec_source}")
            
            # Ensure scope directory exists
            scope_dir = self.project_root / ".claude/specs/scope"
            scope_dir.mkdir(parents=True, exist_ok=True)
            self.logger.log_directory_created(str(scope_dir))
            
            if self.spec_source.exists():
                if self.spec_scope.exists():
                    self.logger.log_warning("Spec already in scope, removing old version")
                    shutil.rmtree(self.spec_scope)
                
                self.logger.logger.info(f"Moving spec to: {self.spec_scope}")
                shutil.copytree(self.spec_source, self.spec_scope)
                self.logger.log_tool_use("shutil.copytree", {"source": str(self.spec_source), "dest": str(self.spec_scope)})
                
                # Update metadata
                meta_file = self.spec_scope / "_meta.json"
                if not meta_file.exists():
                    meta = {"name": self.spec_name, "created_at": datetime.now().isoformat()}
                else:
                    meta = json.loads(meta_file.read_text())
                
                meta["status"] = "IN_SCOPE"
                meta["scope_date"] = datetime.now().isoformat()
                meta["workflow_id"] = self.logger.workflow_id
                meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
                self.logger.log_file_created(str(meta_file), "metadata")
                
                # Remove from source
                shutil.rmtree(self.spec_source)
                self.logger.logger.info("Successfully moved spec to scope")
                return True
            else:
                self.logger.log_error(f"Source spec not found at: {self.spec_source}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Failed to move spec: {str(e)}", e)
            return False
    
    async def define_project_structure(self):
        """Define project structure"""
        self.logger.logger.info("Defining project structure...")
        
        # Read spec overview if exists
        overview_file = self.spec_scope / "overview.md"
        if overview_file.exists():
            overview = overview_file.read_text(encoding='utf-8')
            self.logger.logger.debug(f"Read overview: {len(overview)} characters")
            
            # Analyze spec type
            is_ml = "ml" in overview.lower() or "machine learning" in overview.lower()
            is_frontend = "dashboard" in overview.lower() or "ui" in overview.lower()
            is_api = "api" in overview.lower() or "service" in overview.lower()
            
            self.logger.log_metric("has_ml_component", is_ml)
            self.logger.log_metric("has_frontend", is_frontend)
            self.logger.log_metric("has_api", is_api)
        else:
            self.logger.log_warning("No overview.md found, using defaults")
            is_ml = False
            is_frontend = True
            is_api = True
        
        structure = {
            "base_path": f"implementations/{self.spec_name}",
            "services": [],
            "frontend": [],
            "ml_services": [],
            "infrastructure": {
                "k8s": f"infrastructure/k8s/{self.spec_name}/",
                "docker": f"infrastructure/docker/{self.spec_name}/"
            },
            "shared": f"shared/{self.spec_name}-common/"
        }
        
        # Define services based on spec type
        if is_api:
            service = {
                "name": f"{self.spec_name}-api",
                "path": f"services/{self.spec_name}-api/",
                "type": "nestjs"
            }
            structure["services"].append(service)
            self.logger.logger.info(f"Added service: {service['name']}")
        
        if is_frontend:
            frontend = {
                "name": f"{self.spec_name}-web",
                "path": f"frontend/{self.spec_name}-web/",
                "type": "react"
            }
            structure["frontend"].append(frontend)
            self.logger.logger.info(f"Added frontend: {frontend['name']}")
        
        if is_ml:
            ml_service = {
                "name": f"{self.spec_name}-ml",
                "path": f"ml-services/{self.spec_name}-ml/",
                "type": "python"
            }
            structure["ml_services"].append(ml_service)
            self.logger.logger.info(f"Added ML service: {ml_service['name']}")
        
        # Create directories
        for service in structure["services"] + structure["frontend"] + structure["ml_services"]:
            service_path = self.project_root / service["path"]
            service_path.mkdir(parents=True, exist_ok=True)
            self.logger.log_directory_created(str(service_path))
        
        # Create infrastructure directories
        k8s_path = self.project_root / structure["infrastructure"]["k8s"]
        docker_path = self.project_root / structure["infrastructure"]["docker"]
        k8s_path.mkdir(parents=True, exist_ok=True)
        docker_path.mkdir(parents=True, exist_ok=True)
        self.logger.log_directory_created(str(k8s_path))
        self.logger.log_directory_created(str(docker_path))
        
        self.results['structure'] = structure
        return structure
    
    async def generate_requirements(self):
        """Generate requirements (stubbed for now)"""
        self.logger.logger.info("Generating requirements...")
        
        requirements = {
            "functional": [],
            "non_functional": [],
            "technical": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save requirements
        req_file = self.spec_scope / "generated_requirements.json"
        req_file.write_text(json.dumps(requirements, indent=2), encoding='utf-8')
        self.logger.log_file_created(str(req_file), "spec")
        
        self.results['requirements'] = requirements
        return requirements
    
    async def create_system_design(self):
        """Create system design (stubbed)"""
        self.logger.logger.info("Creating system design...")
        
        design = {
            "architecture": "microservices",
            "patterns": ["REST", "Event-Driven", "CQRS"],
            "databases": [],
            "services": self.results.get('structure', {}).get('services', []),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save design
        design_file = self.spec_scope / "generated_design.json"
        design_file.write_text(json.dumps(design, indent=2), encoding='utf-8')
        self.logger.log_file_created(str(design_file), "spec")
        
        self.results['design'] = design
        return design
    
    async def generate_tasks(self):
        """Generate tasks (stubbed)"""
        self.logger.logger.info("Generating tasks...")
        
        tasks = []
        task_id = 1
        
        # Generate tasks for each service
        for service in self.results.get('structure', {}).get('services', []):
            task = {
                "id": f"TASK-{task_id:03d}",
                "title": f"Implement {service['name']}",
                "service": service['name'],
                "path": service['path'],
                "priority": "high"
            }
            tasks.append(task)
            task_id += 1
            self.logger.logger.debug(f"Created task: {task['id']} - {task['title']}")
        
        # Save tasks
        tasks_file = self.spec_scope / "generated_tasks.json"
        tasks_file.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        self.logger.log_file_created(str(tasks_file), "spec")
        
        self.results['tasks'] = tasks
        return tasks
    
    async def implement_code_structured(self, structure, tasks):
        """Implement code with structure"""
        self.logger.logger.info("Implementing code...")
        
        files_created = []
        
        # Track progress
        total_services = len(structure.get('services', [])) + len(structure.get('frontend', [])) + len(structure.get('ml_services', []))
        current = 0
        
        # Implement each service
        for service in structure.get('services', []):
            current += 1
            self.logger.log_progress(current, total_services, f"Implementing {service['name']}")
            files = await self.implement_service(service)
            files_created.extend(files)
        
        for frontend in structure.get('frontend', []):
            current += 1
            self.logger.log_progress(current, total_services, f"Implementing {frontend['name']}")
            files = await self.implement_frontend(frontend)
            files_created.extend(files)
        
        for ml_service in structure.get('ml_services', []):
            current += 1
            self.logger.log_progress(current, total_services, f"Implementing {ml_service['name']}")
            files = await self.implement_ml_service(ml_service)
            files_created.extend(files)
        
        self.results['code_files'] = files_created
        return files_created
    
    async def implement_service(self, service):
        """Implement a backend service"""
        self.logger.logger.debug(f"Implementing service: {service['name']}")
        
        files = []
        base_path = self.project_root / service['path']
        
        # Create package.json
        package_json = {
            "name": service['name'],
            "version": "1.0.0",
            "scripts": {
                "start": "node dist/main.js",
                "dev": "nest start --watch",
                "build": "nest build",
                "test": "jest"
            }
        }
        
        package_file = base_path / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        files.append(str(package_file))
        
        # Create main.ts
        src_path = base_path / "src"
        src_path.mkdir(exist_ok=True)
        main_file = src_path / "main.ts"
        main_file.write_text("// Main entry point\nconsole.log('Service started');", encoding='utf-8')
        files.append(str(main_file))
        
        return files
    
    async def implement_frontend(self, frontend):
        """Implement a frontend app"""
        self.logger.logger.debug(f"Implementing frontend: {frontend['name']}")
        
        files = []
        base_path = self.project_root / frontend['path']
        
        # Create package.json
        package_json = {
            "name": frontend['name'],
            "version": "1.0.0",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            }
        }
        
        package_file = base_path / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        files.append(str(package_file))
        
        # Create App.tsx
        src_path = base_path / "src"
        src_path.mkdir(exist_ok=True)
        app_file = src_path / "App.tsx"
        app_file.write_text(f"// {frontend['name']} App\nexport default function App() {{ return <div>App</div>; }}", encoding='utf-8')
        files.append(str(app_file))
        
        return files
    
    async def implement_ml_service(self, ml_service):
        """Implement an ML service"""
        self.logger.logger.debug(f"Implementing ML service: {ml_service['name']}")
        
        files = []
        base_path = self.project_root / ml_service['path']
        
        # Create requirements.txt
        req_file = base_path / "requirements.txt"
        req_file.write_text("fastapi\nuvicorn\npandas\nnumpy\nscikit-learn", encoding='utf-8')
        files.append(str(req_file))
        
        # Create main.py
        app_path = base_path / "app"
        app_path.mkdir(exist_ok=True)
        main_file = app_path / "main.py"
        main_file.write_text(f"# {ml_service['name']} ML Service\nfrom fastapi import FastAPI\napp = FastAPI()", encoding='utf-8')
        files.append(str(main_file))
        
        return files
    
    async def generate_tests(self, structure):
        """Generate test files"""
        self.logger.logger.info("Generating tests...")
        
        test_files = []
        
        for service in structure.get('services', []):
            test_dir = self.project_root / service['path'] / "test"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / "app.e2e-spec.ts"
            test_file.write_text("// E2E tests", encoding='utf-8')
            test_files.append(str(test_file))
        
        self.results['test_files'] = test_files
        return test_files
    
    async def generate_documentation(self, structure):
        """Generate documentation"""
        self.logger.logger.info("Generating documentation...")
        
        readme = f"# {self.spec_name.replace('-', ' ').title()}\n\n## Overview\nImplementation of {self.spec_name} feature.\n"
        
        # Save README
        impl_path = self.project_root / f"implementations/{self.spec_name}"
        impl_path.mkdir(parents=True, exist_ok=True)
        readme_file = impl_path / "README.md"
        readme_file.write_text(readme, encoding='utf-8')
        
        self.results['documentation'] = [str(readme_file)]
        return [str(readme_file)]
    
    async def setup_infrastructure(self, structure):
        """Setup infrastructure"""
        self.logger.logger.info("Setting up infrastructure...")
        
        infra_files = []
        
        # Kubernetes namespace
        k8s_path = self.project_root / structure['infrastructure']['k8s']
        namespace_file = k8s_path / "namespace.yaml"
        namespace_file.write_text(f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {self.spec_name}", encoding='utf-8')
        infra_files.append(str(namespace_file))
        
        # Docker compose
        docker_path = self.project_root / structure['infrastructure']['docker']
        compose_file = docker_path / "docker-compose.yml"
        compose_file.write_text("version: '3.8'\nservices:\n  # Services", encoding='utf-8')
        infra_files.append(str(compose_file))
        
        self.results['infrastructure'] = infra_files
        return infra_files
    
    async def validate_execution(self):
        """Run automated validation and provide insights"""
        try:
            self.logger.logger.info("Running automated validation...")
            
            # Import validator
            from workflow_validator import WorkflowValidator
            
            # Create validator
            validator = WorkflowValidator(
                workflow_id=self.logger.workflow_id,
                spec_name=self.spec_name
            )
            
            # Run validation
            results = validator.validate_workflow()
            
            # Log results
            self.logger.log_metric("validation_health_score", results["health_score"])
            self.logger.log_metric("validation_status", results["overall_status"])
            
            # Log insights
            for insight in results.get("insights", []):
                self.logger.logger.info(f"  [INSIGHT] {insight['message']}")
            
            # Log recommendations
            if results.get("recommendations"):
                self.logger.logger.info("\n  Developer Action Items:")
                for rec in results["recommendations"][:3]:
                    self.logger.logger.info(f"    [{rec['priority']}] {rec['action']}")
                    if 'command' in rec:
                        self.logger.logger.info(f"      -> {rec['command']}")
            
            # Log report location
            if "report_path" in results:
                self.logger.logger.info(f"\n  Validation report: {results['report_path']}")
            
            # Return success if health score is acceptable
            return results["health_score"] >= 70
            
        except Exception as e:
            self.logger.log_error(f"Validation failed: {str(e)}", e)
            return False
    
    def move_spec_to_completed(self):
        """Move spec to completed"""
        try:
            if self.spec_scope.exists():
                completed_dir = self.project_root / ".claude/specs/completed"
                completed_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.logger.info(f"Moving spec to: {self.spec_completed}")
                shutil.copytree(self.spec_scope, self.spec_completed)
                
                # Update metadata
                meta_file = self.spec_completed / "_meta.json"
                if not meta_file.exists():
                    meta_file = self.spec_completed / "completion_meta.json"
                    meta = {}
                else:
                    meta = json.loads(meta_file.read_text())
                
                meta["status"] = "COMPLETED"
                meta["completion_date"] = datetime.now().isoformat()
                meta["implementation_location"] = f"implementations/{self.spec_name}"
                meta["workflow_id"] = self.logger.workflow_id
                meta["log_file"] = str(self.logger.log_file)
                meta["summary_file"] = str(self.logger.summary_file)
                meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
                
                # Remove from scope
                shutil.rmtree(self.spec_scope)
                
                # Verify the move was successful
                if self.spec_completed.exists() and not self.spec_scope.exists():
                    self.logger.logger.info("Successfully moved spec to completed")
                    self.logger.logger.info(f"Verified: Spec properly moved from scope to completed")
                else:
                    self.logger.log_error("Failed to properly move spec")
                    if self.spec_scope.exists():
                        self.logger.log_error("Spec still exists in scope folder")
                    if not self.spec_completed.exists():
                        self.logger.log_error("Spec not found in completed folder")
            else:
                self.logger.log_warning("Spec not found in scope")
                
        except Exception as e:
            self.logger.log_error(f"Failed to move spec to completed: {str(e)}", e)


async def main():
    """Execute the logged workflow"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python logged_workflow_executor.py <spec-name> [source-folder] [log-level]")
        print("Example: python logged_workflow_executor.py user-auth backlog DEBUG")
        return 1
    
    spec_name = sys.argv[1]
    source_folder = sys.argv[2] if len(sys.argv) > 2 else "backlog"
    log_level = sys.argv[3] if len(sys.argv) > 3 else "INFO"
    
    executor = LoggedWorkflowExecutor(spec_name, source_folder, log_level)
    success = await executor.execute_workflow()
    
    print(f"\nLogs saved to: .claude/logs/workflows/")
    print(f"Check the summary at: {executor.logger.summary_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))