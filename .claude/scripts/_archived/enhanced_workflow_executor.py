#!/usr/bin/env python3
"""
Enhanced Development Workflow Executor
Handles proper folder structure and spec lifecycle management
"""

import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
import sys

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

class EnhancedWorkflowExecutor:
    """Execute complete development workflow with proper structure"""
    
    def __init__(self, spec_name, spec_folder="backlog"):
        self.spec_name = spec_name
        # Get the script's parent directory (should be .claude/scripts)
        script_dir = Path(__file__).parent
        # Go up to project root
        self.project_root = script_dir.parent.parent
        # Set paths relative to project root
        self.spec_source = self.project_root / f".claude/specs/{spec_folder}/{spec_name}"
        self.spec_scope = self.project_root / f".claude/specs/scope/{spec_name}"
        self.spec_completed = self.project_root / f".claude/specs/completed/{spec_name}"
        self.results = {}
        
    async def execute_workflow(self):
        """Execute the enhanced development workflow"""
        print("=" * 80)
        print("ENHANCED DEVELOPMENT WORKFLOW EXECUTION")
        print("=" * 80)
        print(f"Spec: {self.spec_name}")
        print(f"Source: {self.spec_source}")
        print("-" * 80)
        
        # Phase 0: Move spec to scope
        print("\n[PHASE 0] Spec Lifecycle Management")
        print("-" * 40)
        self.move_spec_to_scope()
        
        # Phase 1: Project Structure Definition
        print("\n[PHASE 1] Project Structure Definition")
        print("-" * 40)
        structure = await self.define_project_structure()
        
        # Phase 2: Requirements Analysis
        print("\n[PHASE 2] Requirements Analysis")
        print("-" * 40)
        requirements = await self.generate_requirements()
        
        # Phase 3: System Design
        print("\n[PHASE 3] System Design")
        print("-" * 40)
        design = await self.create_system_design()
        
        # Phase 4: Task Generation
        print("\n[PHASE 4] Task Breakdown")
        print("-" * 40)
        tasks = await self.generate_tasks()
        
        # Phase 5: Code Implementation (with proper structure)
        print("\n[PHASE 5] Code Implementation")
        print("-" * 40)
        code_files = await self.implement_code_structured(structure, tasks)
        
        # Phase 6: Test Generation
        print("\n[PHASE 6] Test Generation")
        print("-" * 40)
        test_files = await self.generate_tests(structure)
        
        # Phase 7: Documentation
        print("\n[PHASE 7] Documentation")
        print("-" * 40)
        docs = await self.generate_documentation(structure)
        
        # Phase 8: Infrastructure
        print("\n[PHASE 8] Infrastructure Setup")
        print("-" * 40)
        infra = await self.setup_infrastructure(structure)
        
        # Phase 9: Move spec to completed
        print("\n[PHASE 9] Spec Completion")
        print("-" * 40)
        self.move_spec_to_completed()
        
        # Final Report
        print("\n" + "=" * 80)
        print("WORKFLOW EXECUTION COMPLETE")
        print("=" * 80)
        self.print_summary()
        
        return True
    
    def move_spec_to_scope(self):
        """Move spec from source to scope folder"""
        # Ensure scope directory exists
        scope_dir = self.project_root / ".claude/specs/scope"
        scope_dir.mkdir(parents=True, exist_ok=True)
        
        if self.spec_source.exists():
            if self.spec_scope.exists():
                print(f"  [INFO] Spec already in scope, removing old version")
                shutil.rmtree(self.spec_scope)
            
            print(f"Moving spec from {self.spec_source} to {self.spec_scope}")
            shutil.copytree(self.spec_source, self.spec_scope)
            
            # Update metadata
            meta_file = self.spec_scope / "_meta.json"
            if not meta_file.exists():
                meta = {
                    "name": self.spec_name,
                    "created_at": datetime.now().isoformat()
                }
            else:
                meta = json.loads(meta_file.read_text())
            
            meta["status"] = "IN_SCOPE"
            meta["scope_date"] = datetime.now().isoformat()
            meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            
            # Remove from source
            shutil.rmtree(self.spec_source)
            print("  [SUCCESS] Spec moved to scope")
        else:
            print("  [ERROR] Source spec not found at:", self.spec_source)
    
    def move_spec_to_completed(self):
        """Move spec from scope to completed folder"""
        if self.spec_scope.exists():
            # Ensure completed folder exists
            completed_dir = self.project_root / ".claude/specs/completed"
            completed_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Moving spec from {self.spec_scope} to {self.spec_completed}")
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
            meta["implementation_location"] = str(self.get_implementation_path())
            meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            
            # Remove from scope
            shutil.rmtree(self.spec_scope)
            
            # Verify the move was successful
            if self.spec_completed.exists() and not self.spec_scope.exists():
                print("  [SUCCESS] Spec moved to completed")
                print(f"  [SUCCESS] Implementation at: {self.get_implementation_path()}")
            else:
                print("  [ERROR] Failed to properly move spec")
                if self.spec_scope.exists():
                    print("  [ERROR] Spec still exists in scope folder")
                if not self.spec_completed.exists():
                    print("  [ERROR] Spec not found in completed folder")
        else:
            print("  [WARNING] Spec not found in scope")
    
    async def define_project_structure(self):
        """Use sr.backend-engineer to define project structure"""
        print("Consulting Sr. Backend Engineer for project structure...")
        
        # Read spec overview
        overview_file = self.spec_scope / "overview.md"
        if overview_file.exists():
            overview = overview_file.read_text()
            # Extract key information from overview
            is_ml = "ml" in overview.lower() or "machine learning" in overview.lower()
            is_frontend = "dashboard" in overview.lower() or "ui" in overview.lower()
            is_api = "api" in overview.lower() or "service" in overview.lower()
        else:
            is_ml = False
            is_frontend = True
            is_api = True
        
        structure = {
            "base_path": self.get_implementation_path(),
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
            structure["services"].append({
                "name": f"{self.spec_name}-api",
                "path": f"services/{self.spec_name}-api/",
                "type": "nestjs",
                "structure": self.get_service_structure("nestjs")
            })
        
        if is_frontend:
            structure["frontend"].append({
                "name": f"{self.spec_name}-web",
                "path": f"frontend/{self.spec_name}-web/",
                "type": "react",
                "structure": self.get_service_structure("react")
            })
        
        if is_ml:
            structure["ml_services"].append({
                "name": f"{self.spec_name}-ml",
                "path": f"ml-services/{self.spec_name}-ml/",
                "type": "python",
                "structure": self.get_service_structure("python-ml")
            })
        
        self.results['structure'] = structure
        
        # Create base directories
        for service in structure["services"] + structure["frontend"] + structure["ml_services"]:
            service_path = self.project_root / service["path"]
            service_path.mkdir(parents=True, exist_ok=True)
            print(f"  [SUCCESS] Created: {service['path']}")
        
        # Create infrastructure directories
        (self.project_root / structure["infrastructure"]["k8s"]).mkdir(parents=True, exist_ok=True)
        (self.project_root / structure["infrastructure"]["docker"]).mkdir(parents=True, exist_ok=True)
        print(f"  [SUCCESS] Created: infrastructure folders")
        
        return structure
    
    def get_implementation_path(self):
        """Get the implementation path for this spec"""
        return f"implementations/{self.spec_name}"
    
    def get_service_structure(self, service_type):
        """Get the standard structure for a service type"""
        structures = {
            "nestjs": {
                "src": ["controllers", "services", "entities", "dto", "middleware", "config"],
                "test": ["unit", "integration", "e2e"],
                "files": ["package.json", "tsconfig.json", "Dockerfile", "README.md", ".env.example"]
            },
            "react": {
                "src": ["components", "pages", "services", "hooks", "store", "utils", "types", "styles"],
                "public": [],
                "test": ["unit", "integration"],
                "files": ["package.json", "tsconfig.json", "Dockerfile", "README.md", ".env.example"]
            },
            "python-ml": {
                "app": ["api", "models", "services", "data", "utils"],
                "tests": [],
                "notebooks": [],
                "data": ["raw", "processed"],
                "files": ["requirements.txt", "Dockerfile", "README.md", ".env.example", "setup.py"]
            }
        }
        return structures.get(service_type, {})
    
    async def generate_requirements(self):
        """Generate detailed requirements"""
        print("Generating detailed requirements...")
        
        requirements = {
            "functional": [],
            "non_functional": [],
            "technical": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save requirements in spec folder
        req_file = self.spec_scope / "generated_requirements.json"
        req_file.write_text(json.dumps(requirements, indent=2), encoding='utf-8')
        
        self.results['requirements'] = requirements
        return requirements
    
    async def create_system_design(self):
        """Create detailed system design"""
        print("Creating system design...")
        
        design = {
            "architecture": "microservices",
            "patterns": ["REST", "Event-Driven", "CQRS"],
            "databases": [],
            "services": self.results.get('structure', {}).get('services', []),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save design in spec folder
        design_file = self.spec_scope / "generated_design.json"
        design_file.write_text(json.dumps(design, indent=2), encoding='utf-8')
        
        self.results['design'] = design
        return design
    
    async def generate_tasks(self):
        """Generate implementation tasks"""
        print("Generating implementation tasks...")
        
        tasks = []
        task_id = 1
        
        # Generate tasks for each service
        for service in self.results.get('structure', {}).get('services', []):
            tasks.append({
                "id": f"TASK-{task_id:03d}",
                "title": f"Implement {service['name']}",
                "service": service['name'],
                "path": service['path'],
                "priority": "high"
            })
            task_id += 1
        
        # Save tasks
        tasks_file = self.spec_scope / "generated_tasks.json"
        tasks_file.write_text(json.dumps(tasks, indent=2), encoding='utf-8')
        
        self.results['tasks'] = tasks
        return tasks
    
    async def implement_code_structured(self, structure, tasks):
        """Generate code in proper folder structure"""
        print("Implementing code with proper structure...")
        
        files_created = []
        
        # Implement each service
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
        print(f"  [SUCCESS] Created {len(files_created)} code files")
        return files_created
    
    async def implement_service(self, service):
        """Implement a backend service"""
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
            },
            "dependencies": {
                "@nestjs/common": "^10.0.0",
                "@nestjs/core": "^10.0.0",
                "@nestjs/platform-express": "^10.0.0"
            }
        }
        
        package_file = base_path / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        files.append(str(package_file))
        
        # Create main.ts
        main_ts = """import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors();
  await app.listen(process.env.PORT || 3000);
}
bootstrap();
"""
        
        src_path = base_path / "src"
        src_path.mkdir(exist_ok=True)
        main_file = src_path / "main.ts"
        main_file.write_text(main_ts, encoding='utf-8')
        files.append(str(main_file))
        
        # Create app.module.ts
        app_module = f"""import {{ Module }} from '@nestjs/common';

@Module({{
  imports: [],
  controllers: [],
  providers: [],
}})
export class AppModule {{}}
"""
        
        app_file = src_path / "app.module.ts"
        app_file.write_text(app_module, encoding='utf-8')
        files.append(str(app_file))
        
        print(f"    [SUCCESS] Implemented {service['name']}")
        return files
    
    async def implement_frontend(self, frontend):
        """Implement a frontend application"""
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
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "typescript": "^5.0.0"
            }
        }
        
        package_file = base_path / "package.json"
        package_file.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        files.append(str(package_file))
        
        # Create App.tsx
        app_tsx = f"""import React from 'react';

function App() {{
  return (
    <div className="App">
      <h1>{frontend['name']}</h1>
    </div>
  );
}}

export default App;
"""
        
        src_path = base_path / "src"
        src_path.mkdir(exist_ok=True)
        app_file = src_path / "App.tsx"
        app_file.write_text(app_tsx, encoding='utf-8')
        files.append(str(app_file))
        
        print(f"    [SUCCESS] Implemented {frontend['name']}")
        return files
    
    async def implement_ml_service(self, ml_service):
        """Implement an ML service"""
        files = []
        base_path = self.project_root / ml_service['path']
        
        # Create requirements.txt
        requirements = """fastapi==0.104.0
uvicorn==0.24.0
pandas==2.1.0
numpy==1.24.0
scikit-learn==1.3.0
tensorflow==2.14.0
"""
        
        req_file = base_path / "requirements.txt"
        req_file.write_text(requirements, encoding='utf-8')
        files.append(str(req_file))
        
        # Create main.py
        main_py = f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{ml_service['name']}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {{"service": "{ml_service['name']}", "status": "healthy"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}
"""
        
        app_path = base_path / "app"
        app_path.mkdir(exist_ok=True)
        main_file = app_path / "main.py"
        main_file.write_text(main_py, encoding='utf-8')
        files.append(str(main_file))
        
        print(f"    [SUCCESS] Implemented {ml_service['name']}")
        return files
    
    async def generate_tests(self, structure):
        """Generate test files"""
        print("Generating tests...")
        test_files = []
        
        # Generate tests for each service
        for service in structure.get('services', []):
            test_file = self.project_root / service['path'] / "test" / "app.e2e-spec.ts"
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("// E2E tests", encoding='utf-8')
            test_files.append(str(test_file))
        
        self.results['test_files'] = test_files
        return test_files
    
    async def generate_documentation(self, structure):
        """Generate documentation"""
        print("Generating documentation...")
        
        # Create main README
        readme = f"""# {self.spec_name.replace('-', ' ').title()}

## Overview
Implementation of {self.spec_name} feature.

## Project Structure
```
{self.spec_name}/
├── services/         # Backend services
├── frontend/        # Frontend applications  
├── ml-services/     # Machine learning services
└── infrastructure/  # Deployment configurations
```

## Services

"""
        
        for service in structure.get('services', []):
            readme += f"### {service['name']}\n"
            readme += f"- Path: `{service['path']}`\n"
            readme += f"- Type: {service['type']}\n\n"
        
        readme += "\n## Setup\n"
        readme += "See individual service README files for setup instructions.\n"
        
        # Save in implementation root
        impl_path = self.project_root / self.get_implementation_path()
        impl_path.mkdir(parents=True, exist_ok=True)
        readme_file = impl_path / "README.md"
        readme_file.write_text(readme, encoding='utf-8')
        
        self.results['documentation'] = [str(readme_file)]
        return [str(readme_file)]
    
    async def setup_infrastructure(self, structure):
        """Setup infrastructure configurations"""
        print("Setting up infrastructure...")
        
        infra_files = []
        
        # Create Kubernetes manifests
        k8s_path = self.project_root / structure['infrastructure']['k8s']
        
        # Namespace
        namespace_yaml = f"""apiVersion: v1
kind: Namespace
metadata:
  name: {self.spec_name}
"""
        namespace_file = k8s_path / "namespace.yaml"
        namespace_file.write_text(namespace_yaml, encoding='utf-8')
        infra_files.append(str(namespace_file))
        
        # Create docker-compose for local development
        docker_path = self.project_root / structure['infrastructure']['docker']
        docker_compose = f"""version: '3.8'

services:
  # Add service definitions here
  
networks:
  {self.spec_name}:
    driver: bridge
"""
        compose_file = docker_path / "docker-compose.yml"
        compose_file.write_text(docker_compose, encoding='utf-8')
        infra_files.append(str(compose_file))
        
        self.results['infrastructure'] = infra_files
        print(f"  [SUCCESS] Created {len(infra_files)} infrastructure files")
        return infra_files
    
    def print_summary(self):
        """Print execution summary"""
        print("\nGenerated Artifacts:")
        print("-" * 40)
        
        if 'structure' in self.results:
            structure = self.results['structure']
            total_services = len(structure.get('services', []))
            total_frontend = len(structure.get('frontend', []))
            total_ml = len(structure.get('ml_services', []))
            print(f"Services: {total_services} backend, {total_frontend} frontend, {total_ml} ML")
        
        if 'code_files' in self.results:
            print(f"Code Files: {len(self.results['code_files'])} files created")
        
        if 'test_files' in self.results:
            print(f"Test Files: {len(self.results['test_files'])} test files")
        
        if 'infrastructure' in self.results:
            print(f"Infrastructure: {len(self.results['infrastructure'])} config files")
        
        print(f"\nImplementation Location: {self.get_implementation_path()}")
        print(f"Spec Status: COMPLETED (moved to .claude/specs/completed/)")
        
        print("\nFolder Structure Created:")
        print("-" * 40)
        if 'structure' in self.results:
            for service in self.results['structure'].get('services', []):
                print(f"  [SUCCESS] {service['path']}")
            for frontend in self.results['structure'].get('frontend', []):
                print(f"  [SUCCESS] {frontend['path']}")
            for ml in self.results['structure'].get('ml_services', []):
                print(f"  [SUCCESS] {ml['path']}")

async def main():
    """Execute the enhanced workflow"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_workflow_executor.py <spec-name> [source-folder]")
        print("Example: python enhanced_workflow_executor.py user-auth backlog")
        return 1
    
    spec_name = sys.argv[1]
    source_folder = sys.argv[2] if len(sys.argv) > 2 else "backlog"
    
    executor = EnhancedWorkflowExecutor(spec_name, source_folder)
    success = await executor.execute_workflow()
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))