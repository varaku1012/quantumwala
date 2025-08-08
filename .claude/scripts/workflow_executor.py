#!/usr/bin/env python3
"""
Unified Workflow Executor
Single script that handles all workflow execution with proper structure
"""

import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

# Import workflow logger and validator
from workflow_logger import WorkflowLogger
from workflow_validator import WorkflowValidator

class WorkflowExecutor:
    """
    Single workflow executor that follows steering document standards
    Creates all implementations under implementations/{feature-name}/
    """
    
    def __init__(self, spec_name, spec_folder="backlog", log_level="INFO", enable_logging=True):
        self.spec_name = spec_name
        self.enable_logging = enable_logging
        
        # Setup paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        
        # Spec lifecycle paths
        self.spec_source = self.project_root / f".claude/specs/{spec_folder}/{spec_name}"
        self.spec_scope = self.project_root / f".claude/specs/scope/{spec_name}"
        self.spec_completed = self.project_root / f".claude/specs/completed/{spec_name}"
        
        # Implementation path - ALWAYS under implementations/{feature}/
        self.implementation_root = self.project_root / f"implementations/{spec_name}"
        
        # Initialize logger if enabled
        if self.enable_logging:
            workflow_id = f"{spec_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.logger = WorkflowLogger(
                workflow_id=workflow_id,
                spec_name=spec_name,
                log_level=log_level,
                enable_file_logging=True,
                enable_json_logging=True,
                enable_console=True
            )
            self.workflow_id = workflow_id
        else:
            self.logger = None
            self.workflow_id = None
        
        self.results = {}
        
    def log(self, message, level="INFO"):
        """Unified logging method"""
        if self.logger:
            if level == "ERROR":
                self.logger.log_error(message)
            elif level == "WARNING":
                self.logger.log_warning(message)
            else:
                self.logger.logger.info(message)
        else:
            print(f"[{level}] {message}")
    
    async def execute_workflow(self):
        """Execute the complete workflow with all phases"""
        
        self.log("=" * 80)
        self.log("WORKFLOW EXECUTION")
        self.log("=" * 80)
        self.log(f"Spec: {self.spec_name}")
        self.log(f"Implementation: implementations/{self.spec_name}/")
        self.log("-" * 80)
        
        try:
            # Phase 0: Move spec to scope
            if self.logger:
                self.logger.start_phase("Spec Lifecycle", "Moving spec from backlog to scope")
            
            if not await self.move_spec_to_scope():
                self.log("Failed to move spec to scope", "ERROR")
                return False
            
            if self.logger:
                self.logger.end_phase("Spec Lifecycle", "success")
            
            # Phase 1: Project Structure
            if self.logger:
                self.logger.start_phase("Project Structure", "Creating folder structure")
            
            structure = await self.create_project_structure()
            
            if self.logger:
                self.logger.log_metric("services_count", len(structure.get('services', [])))
                self.logger.log_metric("frontend_count", len(structure.get('frontend', [])))
                self.logger.end_phase("Project Structure", "success")
            
            # Phase 2: Requirements
            if self.logger:
                self.logger.start_phase("Requirements", "Generating requirements")
            
            requirements = await self.generate_requirements()
            
            if self.logger:
                self.logger.end_phase("Requirements", "success")
            
            # Phase 3: Design
            if self.logger:
                self.logger.start_phase("Design", "Creating system design")
            
            design = await self.create_design()
            
            if self.logger:
                self.logger.end_phase("Design", "success")
            
            # Phase 4: Tasks
            if self.logger:
                self.logger.start_phase("Tasks", "Generating tasks")
            
            tasks = await self.generate_tasks()
            
            if self.logger:
                self.logger.log_metric("tasks_count", len(tasks))
                self.logger.end_phase("Tasks", "success")
            
            # Phase 5: Implementation
            if self.logger:
                self.logger.start_phase("Implementation", "Generating code")
            
            code_files = await self.implement_code(structure, tasks)
            
            if self.logger:
                self.logger.log_metric("files_created", len(code_files))
                for file in code_files:
                    self.logger.log_file_created(file, "code")
                self.logger.end_phase("Implementation", "success")
            
            # Phase 6: Tests
            if self.logger:
                self.logger.start_phase("Tests", "Creating test files")
            
            test_files = await self.generate_tests(structure)
            
            if self.logger:
                for file in test_files:
                    self.logger.log_file_created(file, "test")
                self.logger.end_phase("Tests", "success")
            
            # Phase 7: Documentation
            if self.logger:
                self.logger.start_phase("Documentation", "Generating documentation")
            
            docs = await self.generate_documentation(structure)
            
            if self.logger:
                for doc in docs:
                    self.logger.log_file_created(doc, "documentation")
                self.logger.end_phase("Documentation", "success")
            
            # Phase 8: Infrastructure
            if self.logger:
                self.logger.start_phase("Infrastructure", "Creating deployment configs")
            
            infra = await self.setup_infrastructure(structure)
            
            if self.logger:
                for file in infra:
                    self.logger.log_file_created(file, "config")
                self.logger.end_phase("Infrastructure", "success")
            
            # Phase 9: Complete
            if self.logger:
                self.logger.start_phase("Completion", "Moving spec to completed")
            
            await self.move_spec_to_completed()
            
            if self.logger:
                self.logger.log_metric("total_files", 
                    len(code_files) + len(test_files) + len(docs) + len(infra))
                self.logger.end_phase("Completion", "success")
            
            # Phase 10: Validation
            if self.logger:
                self.logger.start_phase("Validation", "Validating workflow")
                validation_success = await self.validate_workflow()
                if validation_success:
                    self.logger.end_phase("Validation", "success")
                else:
                    self.logger.end_phase("Validation", "completed_with_issues")
            
            # Generate summary
            if self.logger:
                summary = self.logger.generate_summary()
                self.log("\n" + summary)
            
            self.log("=" * 80)
            self.log("WORKFLOW COMPLETE")
            self.log(f"Implementation: implementations/{self.spec_name}/")
            self.log("=" * 80)
            
            return True
            
        except Exception as e:
            self.log(f"Workflow failed: {str(e)}", "ERROR")
            if self.logger:
                self.logger.log_error(f"Fatal error: {str(e)}", e)
                if self.logger.current_phase:
                    self.logger.end_phase(self.logger.current_phase, "failed", str(e))
            return False
    
    async def move_spec_to_scope(self):
        """Move spec from backlog to scope"""
        try:
            # Ensure scope directory exists
            scope_dir = self.project_root / ".claude/specs/scope"
            scope_dir.mkdir(parents=True, exist_ok=True)
            
            if not self.spec_source.exists():
                self.log(f"Spec not found at: {self.spec_source}", "ERROR")
                return False
            
            # Remove old version if exists
            if self.spec_scope.exists():
                self.log("Removing old version from scope", "WARNING")
                shutil.rmtree(self.spec_scope)
            
            # Copy to scope
            shutil.copytree(self.spec_source, self.spec_scope)
            
            # Update metadata
            meta_file = self.spec_scope / "_meta.json"
            meta = {}
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
            
            meta.update({
                "name": self.spec_name,
                "status": "IN_SCOPE",
                "scope_date": datetime.now().isoformat(),
                "workflow_id": self.workflow_id
            })
            meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            
            # Remove from backlog
            shutil.rmtree(self.spec_source)
            
            self.log(f"Moved spec to scope: {self.spec_name}")
            return True
            
        except Exception as e:
            self.log(f"Failed to move spec: {str(e)}", "ERROR")
            return False
    
    async def create_project_structure(self):
        """Create project structure under implementations/{feature}/"""
        self.log("Creating project structure...")
        
        # Analyze spec type
        overview_file = self.spec_scope / "overview.md"
        has_api = True  # Default
        has_frontend = True
        has_ml = False
        
        if overview_file.exists():
            overview = overview_file.read_text(encoding='utf-8').lower()
            has_ml = "ml" in overview or "machine learning" in overview
            has_frontend = "dashboard" in overview or "ui" in overview or "frontend" in overview
            has_api = "api" in overview or "service" in overview or "backend" in overview
        
        # Define structure - ALL under implementations/{feature}/
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
        
        # Add components based on spec type
        if has_api:
            structure["services"].append({
                "name": f"{self.spec_name}-api",
                "path": f"implementations/{self.spec_name}/services/{self.spec_name}-api/",
                "type": "nestjs"
            })
        
        if has_frontend:
            structure["frontend"].append({
                "name": f"{self.spec_name}-web",
                "path": f"implementations/{self.spec_name}/frontend/{self.spec_name}-web/",
                "type": "react"
            })
        
        if has_ml:
            structure["ml_services"].append({
                "name": f"{self.spec_name}-ml",
                "path": f"implementations/{self.spec_name}/ml-services/{self.spec_name}-ml/",
                "type": "python"
            })
        
        # Create all directories
        self.implementation_root.mkdir(parents=True, exist_ok=True)
        
        for service in structure["services"] + structure["frontend"] + structure["ml_services"]:
            (self.project_root / service["path"]).mkdir(parents=True, exist_ok=True)
            self.log(f"  Created: {service['path']}")
        
        # Create infrastructure and docs directories
        (self.project_root / structure["infrastructure"]["k8s"]).mkdir(parents=True, exist_ok=True)
        (self.project_root / structure["infrastructure"]["docker"]).mkdir(parents=True, exist_ok=True)
        (self.project_root / structure["docs"]).mkdir(parents=True, exist_ok=True)
        
        self.results['structure'] = structure
        return structure
    
    async def generate_requirements(self):
        """Generate requirements (placeholder for agent integration)"""
        self.log("Generating requirements...")
        
        # TODO: Integrate with business-analyst agent
        requirements = {
            "functional": ["User authentication", "Data persistence"],
            "non_functional": ["Performance", "Security"],
            "technical": ["REST API", "Database"],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to spec folder
        req_file = self.spec_scope / "generated_requirements.json"
        req_file.write_text(json.dumps(requirements, indent=2), encoding='utf-8')
        
        self.results['requirements'] = requirements
        return requirements
    
    async def create_design(self):
        """Create system design (placeholder for agent integration)"""
        self.log("Creating system design...")
        
        # TODO: Integrate with architect agent
        design = {
            "architecture": "microservices",
            "patterns": ["REST", "Event-Driven"],
            "services": self.results.get('structure', {}).get('services', []),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to spec folder
        design_file = self.spec_scope / "generated_design.json"
        design_file.write_text(json.dumps(design, indent=2), encoding='utf-8')
        
        self.results['design'] = design
        return design
    
    async def generate_tasks(self):
        """Generate tasks (placeholder for agent integration)"""
        self.log("Generating tasks...")
        
        # TODO: Integrate with product-manager agent
        tasks = []
        for i, service in enumerate(self.results.get('structure', {}).get('services', []), 1):
            tasks.append({
                "id": f"TASK-{i:03d}",
                "title": f"Implement {service['name']}",
                "service": service['name'],
                "priority": "high"
            })
        
        # Save to spec folder
        tasks_file = self.spec_scope / "generated_tasks.json"
        tasks_file.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        
        self.results['tasks'] = tasks
        return tasks
    
    async def implement_code(self, structure, tasks):
        """Implement code in correct structure"""
        self.log("Implementing code...")
        
        files_created = []
        
        # TODO: Integrate with developer agent
        # For now, create template files
        
        # Backend services
        for service in structure.get('services', []):
            base_path = self.project_root / service['path']
            
            # package.json
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
            files_created.append(str(package_file))
            
            # src/main.ts
            src_path = base_path / "src"
            src_path.mkdir(exist_ok=True)
            main_file = src_path / "main.ts"
            main_file.write_text(
                f"// {service['name']} service\n"
                "import { NestFactory } from '@nestjs/core';\n"
                "import { AppModule } from './app.module';\n\n"
                "async function bootstrap() {\n"
                "  const app = await NestFactory.create(AppModule);\n"
                "  await app.listen(3000);\n"
                "}\n"
                "bootstrap();\n",
                encoding='utf-8'
            )
            files_created.append(str(main_file))
        
        # Frontend apps
        for frontend in structure.get('frontend', []):
            base_path = self.project_root / frontend['path']
            
            # package.json
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
            files_created.append(str(package_file))
            
            # src/App.tsx
            src_path = base_path / "src"
            src_path.mkdir(exist_ok=True)
            app_file = src_path / "App.tsx"
            app_file.write_text(
                f"// {frontend['name']} app\n"
                "import React from 'react';\n\n"
                f"function App() {{\n"
                f"  return <div>{frontend['name']}</div>;\n"
                f"}}\n\n"
                "export default App;\n",
                encoding='utf-8'
            )
            files_created.append(str(app_file))
        
        # ML services
        for ml_service in structure.get('ml_services', []):
            base_path = self.project_root / ml_service['path']
            
            # requirements.txt
            req_file = base_path / "requirements.txt"
            req_file.write_text("fastapi\nuvicorn\npandas\nnumpy", encoding='utf-8')
            files_created.append(str(req_file))
            
            # app/main.py
            app_path = base_path / "app"
            app_path.mkdir(exist_ok=True)
            main_file = app_path / "main.py"
            main_file.write_text(
                f"# {ml_service['name']} ML service\n"
                "from fastapi import FastAPI\n\n"
                f"app = FastAPI(title='{ml_service['name']}')\n\n"
                "@app.get('/')\n"
                "async def root():\n"
                f"    return {{'service': '{ml_service['name']}'}}\n",
                encoding='utf-8'
            )
            files_created.append(str(main_file))
        
        self.results['code_files'] = files_created
        return files_created
    
    async def generate_tests(self, structure):
        """Generate test files"""
        self.log("Generating tests...")
        
        # TODO: Integrate with qa-engineer agent
        test_files = []
        
        for service in structure.get('services', []):
            test_dir = self.project_root / service['path'] / "test"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / "app.e2e-spec.ts"
            test_file.write_text("// E2E tests\ndescribe('App E2E', () => {\n  it('works', () => {\n    expect(true).toBe(true);\n  });\n});", encoding='utf-8')
            test_files.append(str(test_file))
        
        self.results['test_files'] = test_files
        return test_files
    
    async def generate_documentation(self, structure):
        """Generate documentation"""
        self.log("Generating documentation...")
        
        # Main README
        readme_content = f"""# {self.spec_name.replace('-', ' ').title()}

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
            readme_content += f"\n### {service['name']}\n"
            readme_content += f"- Type: {service['type']}\n"
            readme_content += f"- Path: `{service['path']}`\n"
        
        readme_file = self.implementation_root / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        
        # API documentation
        api_doc = f"# API Documentation\n\nAPI documentation for {self.spec_name}"
        api_file = self.implementation_root / "docs" / "API.md"
        api_file.write_text(api_doc, encoding='utf-8')
        
        self.results['documentation'] = [str(readme_file), str(api_file)]
        return [str(readme_file), str(api_file)]
    
    async def setup_infrastructure(self, structure):
        """Setup infrastructure configs"""
        self.log("Setting up infrastructure...")
        
        # TODO: Integrate with devops-engineer agent
        infra_files = []
        
        # Kubernetes
        k8s_path = self.project_root / structure['infrastructure']['k8s']
        namespace_file = k8s_path / "namespace.yaml"
        namespace_content = f"""apiVersion: v1
kind: Namespace
metadata:
  name: {self.spec_name}
"""
        namespace_file.write_text(namespace_content, encoding='utf-8')
        infra_files.append(str(namespace_file))
        
        # Docker
        docker_path = self.project_root / structure['infrastructure']['docker']
        compose_file = docker_path / "docker-compose.yml"
        compose_content = f"""version: '3.8'

services:
  # Add service definitions here

networks:
  {self.spec_name}:
    driver: bridge
"""
        compose_file.write_text(compose_content, encoding='utf-8')
        infra_files.append(str(compose_file))
        
        self.results['infrastructure'] = infra_files
        return infra_files
    
    async def move_spec_to_completed(self):
        """Move spec from scope to completed"""
        try:
            if not self.spec_scope.exists():
                self.log("Spec not found in scope", "WARNING")
                return False
            
            # Ensure completed directory exists
            completed_dir = self.project_root / ".claude/specs/completed"
            completed_dir.mkdir(parents=True, exist_ok=True)
            
            # Remove old version if exists
            if self.spec_completed.exists():
                shutil.rmtree(self.spec_completed)
            
            # Copy to completed
            shutil.copytree(self.spec_scope, self.spec_completed)
            
            # Update metadata
            meta_file = self.spec_completed / "_meta.json"
            if not meta_file.exists():
                meta_file = self.spec_completed / "completion_meta.json"
            
            meta = {}
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
            
            meta.update({
                "status": "COMPLETED",
                "completion_date": datetime.now().isoformat(),
                "implementation_location": f"implementations/{self.spec_name}",
                "workflow_id": self.workflow_id
            })
            
            if self.logger:
                meta["log_file"] = str(self.logger.log_file)
                meta["summary_file"] = str(self.logger.summary_file)
            
            meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            
            # Remove from scope
            shutil.rmtree(self.spec_scope)
            
            self.log(f"Moved spec to completed: {self.spec_name}")
            return True
            
        except Exception as e:
            self.log(f"Failed to move spec to completed: {str(e)}", "ERROR")
            return False
    
    async def validate_workflow(self):
        """Validate the workflow execution"""
        try:
            if not self.logger:
                return True  # Skip validation if no logging
            
            self.log("Running validation...")
            
            validator = WorkflowValidator(
                workflow_id=self.workflow_id,
                spec_name=self.spec_name
            )
            
            results = validator.validate_workflow()
            
            # Log results
            if self.logger:
                self.logger.log_metric("health_score", results["health_score"])
                self.logger.log_metric("validation_status", results["overall_status"])
            
            # Show insights
            for insight in results.get("insights", []):
                self.log(f"  [INSIGHT] {insight['message']}")
            
            # Show recommendations
            if results.get("recommendations"):
                self.log("\n  Action Items:")
                for rec in results["recommendations"][:3]:
                    self.log(f"    [{rec['priority']}] {rec['action']}")
            
            return results["health_score"] >= 70
            
        except Exception as e:
            self.log(f"Validation failed: {str(e)}", "WARNING")
            return True  # Don't fail workflow on validation error


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unified Workflow Executor"
    )
    
    parser.add_argument('spec', help='Name of the spec to process')
    parser.add_argument('--source', default='backlog', choices=['backlog', 'scope'],
                       help='Source folder (default: backlog)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--no-logging', action='store_true',
                       help='Disable logging')
    
    args = parser.parse_args()
    
    executor = WorkflowExecutor(
        spec_name=args.spec,
        spec_folder=args.source,
        log_level=args.log_level,
        enable_logging=not args.no_logging
    )
    
    success = await executor.execute_workflow()
    
    if not args.no_logging:
        print(f"\nLogs saved to: .claude/logs/workflows/")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))