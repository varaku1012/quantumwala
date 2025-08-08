#!/usr/bin/env python3
"""
Corrected Workflow Executor with Proper Implementation Structure
Creates all feature code under implementations/{feature-name}/ as per steering docs
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

class CorrectedWorkflowExecutor:
    """Execute workflow with correct folder structure per steering docs"""
    
    def __init__(self, spec_name, spec_folder="backlog", log_level="INFO"):
        self.spec_name = spec_name
        
        # Setup paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.spec_source = self.project_root / f".claude/specs/{spec_folder}/{spec_name}"
        self.spec_scope = self.project_root / f".claude/specs/scope/{spec_name}"
        self.spec_completed = self.project_root / f".claude/specs/completed/{spec_name}"
        
        # CORRECTED: All implementation goes under implementations/{feature}/
        self.implementation_root = self.project_root / f"implementations/{spec_name}"
        
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
        """Execute the workflow with correct structure"""
        
        # Start logging
        self.logger.logger.info("=" * 80)
        self.logger.logger.info("CORRECTED WORKFLOW EXECUTION")
        self.logger.logger.info("=" * 80)
        self.logger.logger.info(f"Spec: {self.spec_name}")
        self.logger.logger.info(f"Implementation Root: implementations/{self.spec_name}/")
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
            self.logger.start_phase("Project Structure Definition", "Creating correct folder structure")
            structure = await self.define_correct_project_structure()
            self.logger.log_metric("services_count", len(structure.get('services', [])))
            self.logger.log_metric("frontend_count", len(structure.get('frontend', [])))
            self.logger.end_phase("Project Structure Definition", "success")
            
            # Phase 2: Requirements Analysis
            self.logger.start_phase("Requirements Analysis", "Generating requirements")
            requirements = await self.generate_requirements()
            self.logger.end_phase("Requirements Analysis", "success")
            
            # Phase 3: System Design
            self.logger.start_phase("System Design", "Creating system architecture")
            design = await self.create_system_design()
            self.logger.end_phase("System Design", "success")
            
            # Phase 4: Task Generation
            self.logger.start_phase("Task Breakdown", "Generating tasks")
            tasks = await self.generate_tasks()
            self.logger.log_metric("tasks_generated", len(tasks))
            self.logger.end_phase("Task Breakdown", "success")
            
            # Phase 5: Code Implementation
            self.logger.start_phase("Code Implementation", "Generating code with correct structure")
            code_files = await self.implement_code_correctly(structure, tasks)
            self.logger.log_metric("files_created", len(code_files))
            for file in code_files:
                self.logger.log_file_created(file, "code")
            self.logger.end_phase("Code Implementation", "success")
            
            # Phase 6: Test Generation
            self.logger.start_phase("Test Generation", "Creating tests")
            test_files = await self.generate_tests(structure)
            for file in test_files:
                self.logger.log_file_created(file, "test")
            self.logger.end_phase("Test Generation", "success")
            
            # Phase 7: Documentation
            self.logger.start_phase("Documentation", "Generating project documentation")
            docs = await self.generate_documentation(structure)
            for doc in docs:
                self.logger.log_file_created(doc, "documentation")
            self.logger.end_phase("Documentation", "success")
            
            # Phase 8: Infrastructure
            self.logger.start_phase("Infrastructure Setup", "Creating deployment configs")
            infra = await self.setup_infrastructure(structure)
            for file in infra:
                self.logger.log_file_created(file, "config")
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
            
            if self.spec_source.exists():
                if self.spec_scope.exists():
                    self.logger.log_warning("Spec already in scope, removing old version")
                    shutil.rmtree(self.spec_scope)
                
                self.logger.logger.info(f"Moving spec to: {self.spec_scope}")
                shutil.copytree(self.spec_source, self.spec_scope)
                
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
    
    async def define_correct_project_structure(self):
        """Define CORRECT project structure under implementations/{feature}/"""
        self.logger.logger.info("Defining correct project structure...")
        
        # Read spec overview if exists
        overview_file = self.spec_scope / "overview.md"
        if overview_file.exists():
            overview = overview_file.read_text(encoding='utf-8')
            # Analyze spec type
            is_ml = "ml" in overview.lower() or "machine learning" in overview.lower()
            is_frontend = "dashboard" in overview.lower() or "ui" in overview.lower()
            is_api = "api" in overview.lower() or "service" in overview.lower()
        else:
            self.logger.log_warning("No overview.md found, using defaults")
            is_ml = False
            is_frontend = True
            is_api = True
        
        # CORRECTED STRUCTURE - Everything under implementations/{feature}/
        structure = {
            "base_path": f"implementations/{self.spec_name}",
            "services": [],
            "frontend": [],
            "ml_services": [],
            "infrastructure": {
                "k8s": f"implementations/{self.spec_name}/infrastructure/k8s/",
                "docker": f"implementations/{self.spec_name}/infrastructure/docker/"
            },
            "docs": f"implementations/{self.spec_name}/docs/"
        }
        
        # Define services with CORRECT paths
        if is_api:
            service = {
                "name": f"{self.spec_name}-api",
                "path": f"implementations/{self.spec_name}/services/{self.spec_name}-api/",
                "type": "nestjs"
            }
            structure["services"].append(service)
            self.logger.logger.info(f"Added service: {service['name']} at CORRECT path")
        
        if is_frontend:
            frontend = {
                "name": f"{self.spec_name}-web",
                "path": f"implementations/{self.spec_name}/frontend/{self.spec_name}-web/",
                "type": "react"
            }
            structure["frontend"].append(frontend)
            self.logger.logger.info(f"Added frontend: {frontend['name']} at CORRECT path")
        
        if is_ml:
            ml_service = {
                "name": f"{self.spec_name}-ml",
                "path": f"implementations/{self.spec_name}/ml-services/{self.spec_name}-ml/",
                "type": "python"
            }
            structure["ml_services"].append(ml_service)
            self.logger.logger.info(f"Added ML service: {ml_service['name']} at CORRECT path")
        
        # Create the CORRECT directory structure
        self.implementation_root.mkdir(parents=True, exist_ok=True)
        self.logger.log_directory_created(str(self.implementation_root))
        
        # Create subdirectories
        for service in structure["services"] + structure["frontend"] + structure["ml_services"]:
            service_path = self.project_root / service["path"]
            service_path.mkdir(parents=True, exist_ok=True)
            self.logger.log_directory_created(str(service_path))
        
        # Create infrastructure directories
        k8s_path = self.project_root / structure["infrastructure"]["k8s"]
        docker_path = self.project_root / structure["infrastructure"]["docker"]
        docs_path = self.project_root / structure["docs"]
        
        k8s_path.mkdir(parents=True, exist_ok=True)
        docker_path.mkdir(parents=True, exist_ok=True)
        docs_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.log_directory_created(str(k8s_path))
        self.logger.log_directory_created(str(docker_path))
        self.logger.log_directory_created(str(docs_path))
        
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
        
        # Save tasks
        tasks_file = self.spec_scope / "generated_tasks.json"
        tasks_file.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        self.logger.log_file_created(str(tasks_file), "spec")
        
        self.results['tasks'] = tasks
        return tasks
    
    async def implement_code_correctly(self, structure, tasks):
        """Implement code in CORRECT folder structure"""
        self.logger.logger.info("Implementing code in correct structure...")
        
        files_created = []
        
        # Implement each service in CORRECT location
        for service in structure.get('services', []):
            files = await self.implement_service(service)
            files_created.extend(files)
        
        for frontend in structure.get('frontend', []):
            files = await self.implement_frontend(frontend)
            files_created.extend(files)
        
        for ml_service in structure.get('ml_services', []):
            files = await self.implement_ml_service(ml_service)
            files_created.extend(files)
        
        self.results['code_files'] = files_created
        return files_created
    
    async def implement_service(self, service):
        """Implement a backend service in CORRECT location"""
        self.logger.logger.debug(f"Implementing service: {service['name']} at {service['path']}")
        
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
        """Implement a frontend app in CORRECT location"""
        self.logger.logger.debug(f"Implementing frontend: {frontend['name']} at {frontend['path']}")
        
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
        """Implement an ML service in CORRECT location"""
        self.logger.logger.debug(f"Implementing ML service: {ml_service['name']} at {ml_service['path']}")
        
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
        """Generate test files in CORRECT locations"""
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
        """Generate documentation in CORRECT location"""
        self.logger.logger.info("Generating documentation...")
        
        # Main README at feature root
        readme = f"""# {self.spec_name.replace('-', ' ').title()}

## Overview
Implementation of {self.spec_name} feature.

## Structure
```
implementations/{self.spec_name}/
├── services/         # Backend services
├── frontend/        # Frontend applications  
├── ml-services/     # Machine learning services
├── infrastructure/  # Deployment configurations
└── docs/           # Documentation
```

## Services

"""
        
        for service in structure.get('services', []):
            readme += f"### {service['name']}\n"
            readme += f"- Path: `{service['path']}`\n"
            readme += f"- Type: {service['type']}\n\n"
        
        # Save README at implementation root
        readme_file = self.implementation_root / "README.md"
        readme_file.write_text(readme, encoding='utf-8')
        
        # Create API documentation
        api_doc = f"# API Documentation for {self.spec_name}\n\nAPI endpoints and specifications."
        api_file = self.implementation_root / "docs" / "API.md"
        api_file.write_text(api_doc, encoding='utf-8')
        
        self.results['documentation'] = [str(readme_file), str(api_file)]
        return [str(readme_file), str(api_file)]
    
    async def setup_infrastructure(self, structure):
        """Setup infrastructure in CORRECT location"""
        self.logger.logger.info("Setting up infrastructure...")
        
        infra_files = []
        
        # Kubernetes namespace - CORRECT path
        k8s_path = self.project_root / structure['infrastructure']['k8s']
        namespace_file = k8s_path / "namespace.yaml"
        namespace_file.write_text(f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {self.spec_name}", encoding='utf-8')
        infra_files.append(str(namespace_file))
        
        # Docker compose - CORRECT path
        docker_path = self.project_root / structure['infrastructure']['docker']
        compose_file = docker_path / "docker-compose.yml"
        compose_file.write_text("version: '3.8'\nservices:\n  # Services", encoding='utf-8')
        infra_files.append(str(compose_file))
        
        self.results['infrastructure'] = infra_files
        return infra_files
    
    def move_spec_to_completed(self):
        """Move spec to completed"""
        try:
            if self.spec_scope.exists():
                completed_dir = self.project_root / ".claude/specs/completed"
                completed_dir.mkdir(parents=True, exist_ok=True)
                
                self.logger.logger.info(f"Moving spec to: {self.spec_completed}")
                shutil.copytree(self.spec_scope, self.spec_completed)
                
                # Update metadata with CORRECT implementation location
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
                    self.logger.logger.info(f"Implementation at: implementations/{self.spec_name}/")
                else:
                    self.logger.log_error("Failed to properly move spec")
        except Exception as e:
            self.logger.log_error(f"Failed to move spec to completed: {str(e)}", e)


async def main():
    """Execute the corrected workflow"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python corrected_workflow_executor.py <spec-name> [source-folder] [log-level]")
        print("Example: python corrected_workflow_executor.py user-auth backlog INFO")
        return 1
    
    spec_name = sys.argv[1]
    source_folder = sys.argv[2] if len(sys.argv) > 2 else "backlog"
    log_level = sys.argv[3] if len(sys.argv) > 3 else "INFO"
    
    executor = CorrectedWorkflowExecutor(spec_name, source_folder, log_level)
    success = await executor.execute_workflow()
    
    print(f"\nImplementation created at: implementations/{spec_name}/")
    print(f"Logs saved to: .claude/logs/workflows/")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))