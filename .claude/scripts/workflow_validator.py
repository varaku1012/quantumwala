#!/usr/bin/env python3
"""
Workflow Validation and Insights System
Automatically validates workflow execution and provides developer insights
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class WorkflowValidator:
    """
    Validates workflow execution and provides insights
    """
    
    def __init__(self, workflow_id: str = None, spec_name: str = None):
        self.workflow_id = workflow_id
        self.spec_name = spec_name
        
        # Setup paths
        script_dir = Path(__file__).parent
        self.project_root = script_dir.parent.parent
        self.logs_dir = self.project_root / ".claude/logs/workflows"
        self.specs_dir = self.project_root / ".claude/specs"
        
        # Validation results
        self.validation_results = {
            "workflow_id": workflow_id,
            "spec_name": spec_name,
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "health_score": 0,
            "validations": {},
            "issues": [],
            "warnings": [],
            "insights": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Load latest workflow if not specified
        if not workflow_id and spec_name:
            self.load_latest_workflow(spec_name)
    
    def load_latest_workflow(self, spec_name: str):
        """Load the most recent workflow for a spec"""
        pattern = f"*{spec_name}*.json"
        json_files = list(self.logs_dir.glob(pattern))
        
        if json_files:
            # Sort by modification time and get the latest
            latest = max(json_files, key=lambda f: f.stat().st_mtime)
            self.workflow_id = latest.stem
            self.log_file = latest
            self.summary_file = latest.with_suffix('.md')
            return True
        return False
    
    def validate_workflow(self) -> Dict[str, Any]:
        """
        Perform comprehensive workflow validation
        """
        print("\n" + "=" * 80)
        print("WORKFLOW VALIDATION & INSIGHTS")
        print("=" * 80)
        print(f"Spec: {self.spec_name}")
        print(f"Workflow: {self.workflow_id}")
        print("-" * 80)
        
        # 1. Validate Log Files
        print("\n[1/10] Validating log files...")
        self._validate_log_files()
        
        # 2. Validate Spec Movement
        print("[2/10] Validating spec lifecycle...")
        self._validate_spec_lifecycle()
        
        # 3. Validate Generated Code
        print("[3/10] Validating generated code...")
        self._validate_generated_code()
        
        # 4. Validate Project Structure
        print("[4/10] Validating project structure...")
        self._validate_project_structure()
        
        # 5. Validate Phase Execution
        print("[5/10] Validating phase execution...")
        self._validate_phases()
        
        # 6. Validate Agent Calls
        print("[6/10] Validating agent interactions...")
        self._validate_agents()
        
        # 7. Analyze Performance
        print("[7/10] Analyzing performance metrics...")
        self._analyze_performance()
        
        # 8. Check for Errors
        print("[8/10] Checking for errors and issues...")
        self._check_errors()
        
        # 9. Generate Insights
        print("[9/10] Generating insights...")
        self._generate_insights()
        
        # 10. Calculate Health Score
        print("[10/10] Calculating health score...")
        self._calculate_health_score()
        
        # Generate report
        self._generate_report()
        
        return self.validation_results
    
    def _validate_log_files(self):
        """Validate that all expected log files exist"""
        validations = {
            "log_file_exists": False,
            "summary_exists": False,
            "json_log_exists": False,
            "log_readable": False
        }
        
        # Check for log files
        log_pattern = f"*{self.spec_name}*.log"
        json_pattern = f"*{self.spec_name}*.json"
        summary_pattern = f"*{self.spec_name}*summary.md"
        
        log_files = list(self.logs_dir.glob(log_pattern))
        json_files = list(self.logs_dir.glob(json_pattern))
        summary_files = list(self.logs_dir.glob(summary_pattern))
        
        if log_files:
            validations["log_file_exists"] = True
            self.log_file_path = log_files[-1]
        else:
            self.validation_results["issues"].append({
                "type": "MISSING_LOG",
                "severity": "HIGH",
                "message": "No log file found for workflow"
            })
        
        if json_files:
            validations["json_log_exists"] = True
            self.json_log_path = json_files[-1]
            try:
                with open(self.json_log_path, 'r', encoding='utf-8') as f:
                    self.json_log_data = json.load(f)
                    validations["log_readable"] = True
            except:
                self.validation_results["issues"].append({
                    "type": "CORRUPT_LOG",
                    "severity": "HIGH",
                    "message": "JSON log file is corrupted or unreadable"
                })
        
        if summary_files:
            validations["summary_exists"] = True
            self.summary_file_path = summary_files[-1]
        else:
            self.validation_results["warnings"].append({
                "type": "MISSING_SUMMARY",
                "message": "No summary file generated"
            })
        
        self.validation_results["validations"]["log_files"] = validations
    
    def _validate_spec_lifecycle(self):
        """Validate spec moved through correct lifecycle stages"""
        validations = {
            "in_completed": False,
            "has_metadata": False,
            "not_in_backlog": False,
            "not_in_scope": False
        }
        
        # Check completed folder
        completed_path = self.specs_dir / "completed" / self.spec_name
        if completed_path.exists():
            validations["in_completed"] = True
            
            # Check metadata
            meta_file = completed_path / "_meta.json"
            if not meta_file.exists():
                meta_file = completed_path / "completion_meta.json"
            
            if meta_file.exists():
                validations["has_metadata"] = True
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.validation_results["metrics"]["completion_date"] = metadata.get("completion_date")
                    self.validation_results["metrics"]["implementation_location"] = metadata.get("implementation_location")
        else:
            self.validation_results["issues"].append({
                "type": "INCOMPLETE_LIFECYCLE",
                "severity": "MEDIUM",
                "message": "Spec not moved to completed folder"
            })
        
        # Check it's not still in backlog or scope
        backlog_path = self.specs_dir / "backlog" / self.spec_name
        scope_path = self.specs_dir / "scope" / self.spec_name
        
        validations["not_in_backlog"] = not backlog_path.exists()
        validations["not_in_scope"] = not scope_path.exists()
        
        if scope_path.exists():
            self.validation_results["warnings"].append({
                "type": "SPEC_IN_SCOPE",
                "message": "Spec still exists in scope folder - may be incomplete"
            })
        
        self.validation_results["validations"]["spec_lifecycle"] = validations
    
    def _validate_generated_code(self):
        """Validate that code was actually generated"""
        validations = {
            "services_exist": False,
            "frontend_exists": False,
            "has_source_files": False,
            "has_package_files": False,
            "file_count": 0
        }
        
        files_found = []
        
        # Check services
        services_path = self.project_root / "services" / f"{self.spec_name}-api"
        if services_path.exists():
            validations["services_exist"] = True
            # Count files
            for file in services_path.rglob("*"):
                if file.is_file():
                    files_found.append(str(file.relative_to(self.project_root)))
            
            # Check for package.json
            if (services_path / "package.json").exists():
                validations["has_package_files"] = True
            
            # Check for source files
            if (services_path / "src").exists():
                validations["has_source_files"] = True
        else:
            self.validation_results["issues"].append({
                "type": "MISSING_SERVICE",
                "severity": "HIGH",
                "message": f"Service not found at services/{self.spec_name}-api"
            })
        
        # Check frontend
        frontend_path = self.project_root / "frontend" / f"{self.spec_name}-web"
        if frontend_path.exists():
            validations["frontend_exists"] = True
            # Count files
            for file in frontend_path.rglob("*"):
                if file.is_file():
                    files_found.append(str(file.relative_to(self.project_root)))
        
        validations["file_count"] = len(files_found)
        self.validation_results["metrics"]["files_generated"] = len(files_found)
        self.validation_results["metrics"]["generated_files"] = files_found[:10]  # First 10 files
        
        if validations["file_count"] == 0:
            self.validation_results["issues"].append({
                "type": "NO_CODE_GENERATED",
                "severity": "CRITICAL",
                "message": "No code files were generated"
            })
        elif validations["file_count"] < 5:
            self.validation_results["warnings"].append({
                "type": "FEW_FILES",
                "message": f"Only {validations['file_count']} files generated - may be incomplete"
            })
        
        self.validation_results["validations"]["generated_code"] = validations
    
    def _validate_project_structure(self):
        """Validate project structure follows standards"""
        validations = {
            "follows_structure": True,
            "has_infrastructure": False,
            "has_implementation_docs": False,
            "structure_complete": True
        }
        
        # Check infrastructure
        k8s_path = self.project_root / "infrastructure/k8s" / self.spec_name
        docker_path = self.project_root / "infrastructure/docker" / self.spec_name
        
        if k8s_path.exists() or docker_path.exists():
            validations["has_infrastructure"] = True
        else:
            self.validation_results["warnings"].append({
                "type": "MISSING_INFRASTRUCTURE",
                "message": "Infrastructure configurations not generated"
            })
        
        # Check implementation docs
        impl_path = self.project_root / "implementations" / self.spec_name
        if impl_path.exists():
            validations["has_implementation_docs"] = True
            if (impl_path / "README.md").exists():
                self.validation_results["insights"].append({
                    "type": "DOCUMENTATION",
                    "message": "Implementation documentation created successfully"
                })
        else:
            self.validation_results["warnings"].append({
                "type": "MISSING_DOCS",
                "message": "Implementation documentation not created"
            })
        
        self.validation_results["validations"]["project_structure"] = validations
    
    def _validate_phases(self):
        """Validate phase execution from logs"""
        if not hasattr(self, 'json_log_data'):
            return
        
        expected_phases = [
            "Spec Lifecycle Management",
            "Project Structure Definition",
            "Requirements Analysis",
            "System Design",
            "Task Breakdown",
            "Code Implementation",
            "Test Generation",
            "Documentation",
            "Infrastructure Setup",
            "Spec Completion"
        ]
        
        phase_validation = {
            "all_phases_executed": False,
            "phases_successful": 0,
            "phases_failed": 0,
            "missing_phases": []
        }
        
        # Parse log data for phases
        if isinstance(self.json_log_data, list):
            # It's a list of log entries
            phases_found = set()
            for entry in self.json_log_data:
                if "PHASE START:" in entry.get("message", ""):
                    phase_name = entry["message"].split("PHASE START:")[-1].strip()
                    phases_found.add(phase_name)
        elif isinstance(self.json_log_data, dict) and "phases" in self.json_log_data:
            # It's structured log data
            phases_data = self.json_log_data.get("phases", {})
            for phase_name, phase_info in phases_data.items():
                if phase_info.get("status") == "success":
                    phase_validation["phases_successful"] += 1
                else:
                    phase_validation["phases_failed"] += 1
                    self.validation_results["issues"].append({
                        "type": "PHASE_FAILED",
                        "severity": "HIGH",
                        "message": f"Phase '{phase_name}' failed",
                        "details": phase_info.get("error")
                    })
            
            phases_found = set(phases_data.keys())
        else:
            phases_found = set()
        
        # Check for missing phases
        for expected in expected_phases:
            if not any(expected.lower() in found.lower() for found in phases_found):
                phase_validation["missing_phases"].append(expected)
        
        phase_validation["all_phases_executed"] = len(phase_validation["missing_phases"]) == 0
        
        if phase_validation["missing_phases"]:
            self.validation_results["warnings"].append({
                "type": "MISSING_PHASES",
                "message": f"Missing phases: {', '.join(phase_validation['missing_phases'][:3])}"
            })
        
        self.validation_results["validations"]["phases"] = phase_validation
    
    def _validate_agents(self):
        """Validate agent interactions"""
        if not hasattr(self, 'json_log_data'):
            return
        
        agent_validation = {
            "agents_called": 0,
            "agents_successful": 0,
            "agents_failed": 0,
            "expected_agents_called": False
        }
        
        expected_agents = [
            "sr.backend-engineer",
            "business-analyst",
            "architect",
            "product-manager",
            "developer",
            "qa-engineer",
            "devops-engineer"
        ]
        
        agents_found = []
        
        if isinstance(self.json_log_data, dict) and "agents_called" in self.json_log_data:
            agents_data = self.json_log_data.get("agents_called", [])
            agent_validation["agents_called"] = len(agents_data)
            
            for agent_call in agents_data:
                agent_name = agent_call.get("agent", "")
                agents_found.append(agent_name)
                
                if agent_call.get("success", False):
                    agent_validation["agents_successful"] += 1
                else:
                    agent_validation["agents_failed"] += 1
        
        # Check if key agents were called
        missing_agents = []
        for expected in expected_agents:
            if not any(expected in agent for agent in agents_found):
                missing_agents.append(expected)
        
        if len(missing_agents) > 4:  # Most agents missing
            self.validation_results["warnings"].append({
                "type": "NO_AGENT_DELEGATION",
                "message": "Workflow did not use agent delegation - may be using templates only"
            })
        
        agent_validation["expected_agents_called"] = len(missing_agents) < 3
        
        self.validation_results["validations"]["agents"] = agent_validation
    
    def _analyze_performance(self):
        """Analyze performance metrics"""
        metrics = {
            "total_duration": 0,
            "avg_phase_duration": 0,
            "slowest_phase": None,
            "fastest_phase": None,
            "performance_grade": "UNKNOWN"
        }
        
        if hasattr(self, 'json_log_data') and isinstance(self.json_log_data, dict):
            # Get total duration
            if "total_duration_seconds" in self.json_log_data:
                metrics["total_duration"] = self.json_log_data["total_duration_seconds"]
            
            # Analyze phases
            if "phases" in self.json_log_data:
                phases = self.json_log_data["phases"]
                durations = []
                
                for phase_name, phase_data in phases.items():
                    if "duration_seconds" in phase_data:
                        duration = phase_data["duration_seconds"]
                        durations.append((phase_name, duration))
                
                if durations:
                    durations.sort(key=lambda x: x[1])
                    metrics["fastest_phase"] = f"{durations[0][0]} ({durations[0][1]:.2f}s)"
                    metrics["slowest_phase"] = f"{durations[-1][0]} ({durations[-1][1]:.2f}s)"
                    metrics["avg_phase_duration"] = sum(d[1] for d in durations) / len(durations)
        
        # Grade performance
        if metrics["total_duration"] > 0:
            if metrics["total_duration"] < 30:
                metrics["performance_grade"] = "EXCELLENT"
            elif metrics["total_duration"] < 60:
                metrics["performance_grade"] = "GOOD"
            elif metrics["total_duration"] < 120:
                metrics["performance_grade"] = "FAIR"
            else:
                metrics["performance_grade"] = "SLOW"
                self.validation_results["warnings"].append({
                    "type": "SLOW_EXECUTION",
                    "message": f"Workflow took {metrics['total_duration']:.1f}s - consider optimization"
                })
        
        self.validation_results["metrics"]["performance"] = metrics
    
    def _check_errors(self):
        """Check for errors in execution"""
        error_summary = {
            "error_count": 0,
            "warning_count": 0,
            "critical_errors": [],
            "has_failures": False
        }
        
        if hasattr(self, 'json_log_data'):
            if isinstance(self.json_log_data, dict):
                # Check structured log
                errors = self.json_log_data.get("errors", [])
                warnings = self.json_log_data.get("warnings", [])
                
                error_summary["error_count"] = len(errors)
                error_summary["warning_count"] = len(warnings)
                
                for error in errors[:5]:  # First 5 errors
                    error_summary["critical_errors"].append({
                        "phase": error.get("phase"),
                        "message": error.get("message")
                    })
            elif isinstance(self.json_log_data, list):
                # Check log entries
                for entry in self.json_log_data:
                    if entry.get("level") == "ERROR":
                        error_summary["error_count"] += 1
                        if error_summary["error_count"] <= 5:
                            error_summary["critical_errors"].append({
                                "message": entry.get("message", "Unknown error")
                            })
                    elif entry.get("level") == "WARNING":
                        error_summary["warning_count"] += 1
        
        error_summary["has_failures"] = error_summary["error_count"] > 0
        
        if error_summary["has_failures"]:
            self.validation_results["issues"].append({
                "type": "EXECUTION_ERRORS",
                "severity": "HIGH",
                "message": f"Workflow had {error_summary['error_count']} errors",
                "details": error_summary["critical_errors"]
            })
        
        self.validation_results["validations"]["errors"] = error_summary
    
    def _generate_insights(self):
        """Generate actionable insights"""
        
        # Insight: Workflow mode
        if self.validation_results["validations"].get("agents", {}).get("agents_called", 0) == 0:
            self.validation_results["insights"].append({
                "type": "WORKFLOW_MODE",
                "message": "Workflow appears to be running in template mode",
                "recommendation": "Consider using --mode logged or --mode full for better code generation"
            })
        
        # Insight: Performance
        perf = self.validation_results["metrics"].get("performance", {})
        if perf.get("performance_grade") == "EXCELLENT":
            self.validation_results["insights"].append({
                "type": "PERFORMANCE",
                "message": f"Excellent performance - completed in {perf.get('total_duration', 0):.1f}s"
            })
        
        # Insight: Code generation
        file_count = self.validation_results["validations"].get("generated_code", {}).get("file_count", 0)
        if file_count > 10:
            self.validation_results["insights"].append({
                "type": "CODE_GENERATION",
                "message": f"Successfully generated {file_count} files",
                "details": "Code generation completed successfully"
            })
        
        # Insight: Structure compliance
        if self.validation_results["validations"].get("project_structure", {}).get("follows_structure", True):
            self.validation_results["insights"].append({
                "type": "STRUCTURE",
                "message": "Project structure follows steering document standards"
            })
    
    def _calculate_health_score(self):
        """Calculate overall health score"""
        score = 100
        
        # Deduct for issues
        for issue in self.validation_results["issues"]:
            if issue["severity"] == "CRITICAL":
                score -= 25
            elif issue["severity"] == "HIGH":
                score -= 15
            elif issue["severity"] == "MEDIUM":
                score -= 10
        
        # Deduct for warnings
        score -= len(self.validation_results["warnings"]) * 5
        
        # Bonus for good practices
        if self.validation_results["validations"].get("log_files", {}).get("summary_exists"):
            score += 5
        
        if self.validation_results["validations"].get("project_structure", {}).get("has_implementation_docs"):
            score += 5
        
        # Cap between 0 and 100
        score = max(0, min(100, score))
        
        self.validation_results["health_score"] = score
        
        # Determine overall status
        if score >= 90:
            self.validation_results["overall_status"] = "SUCCESS"
        elif score >= 70:
            self.validation_results["overall_status"] = "SUCCESS_WITH_WARNINGS"
        elif score >= 50:
            self.validation_results["overall_status"] = "PARTIAL_SUCCESS"
        else:
            self.validation_results["overall_status"] = "FAILED"
        
        # Add recommendations based on score
        if score < 90:
            if not self.validation_results["validations"].get("generated_code", {}).get("has_source_files"):
                self.validation_results["recommendations"].append({
                    "priority": "HIGH",
                    "action": "Verify code generation completed",
                    "command": f"ls services/{self.spec_name}-api/src/"
                })
            
            if self.validation_results["validations"].get("errors", {}).get("has_failures"):
                self.validation_results["recommendations"].append({
                    "priority": "HIGH",
                    "action": "Review and fix errors in workflow",
                    "command": f"grep ERROR .claude/logs/workflows/*{self.spec_name}*.log"
                })
            
            if not self.validation_results["validations"].get("spec_lifecycle", {}).get("in_completed"):
                self.validation_results["recommendations"].append({
                    "priority": "MEDIUM",
                    "action": "Move spec to completed folder",
                    "command": f"mv .claude/specs/scope/{self.spec_name} .claude/specs/completed/"
                })
            
            if not self.validation_results["validations"].get("project_structure", {}).get("has_infrastructure"):
                self.validation_results["recommendations"].append({
                    "priority": "LOW",
                    "action": "Generate infrastructure configurations",
                    "command": "Consider adding Kubernetes and Docker configs"
                })
    
    def _generate_report(self):
        """Generate validation report"""
        report_path = self.logs_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.spec_name}_validation.md"
        
        report = f"""# Workflow Validation Report

## Summary
- **Spec**: {self.spec_name}
- **Workflow ID**: {self.workflow_id}
- **Status**: {self.validation_results['overall_status']}
- **Health Score**: {self.validation_results['health_score']}/100
- **Timestamp**: {self.validation_results['timestamp']}

## Health Score: {self._get_health_bar(self.validation_results['health_score'])}

## Validation Results

### ✅ Passed Checks
"""
        
        # Add passed validations
        for category, checks in self.validation_results["validations"].items():
            if isinstance(checks, dict):
                for check, value in checks.items():
                    if value is True or (isinstance(value, int) and value > 0):
                        report += f"- {category}.{check}\n"
        
        report += "\n### ❌ Issues Found\n"
        if self.validation_results["issues"]:
            for issue in self.validation_results["issues"]:
                report += f"- **[{issue['severity']}]** {issue['message']}\n"
        else:
            report += "- No critical issues found\n"
        
        report += "\n### ⚠️ Warnings\n"
        if self.validation_results["warnings"]:
            for warning in self.validation_results["warnings"]:
                report += f"- {warning['message']}\n"
        else:
            report += "- No warnings\n"
        
        report += "\n## [INSIGHTS]\n"
        for insight in self.validation_results["insights"]:
            report += f"- **{insight['type']}**: {insight['message']}\n"
        
        report += "\n## [METRICS]\n"
        report += f"- **Files Generated**: {self.validation_results['metrics'].get('files_generated', 0)}\n"
        
        perf = self.validation_results['metrics'].get('performance', {})
        if perf:
            report += f"- **Total Duration**: {perf.get('total_duration', 0):.1f}s\n"
            report += f"- **Performance Grade**: {perf.get('performance_grade', 'N/A')}\n"
            if perf.get('slowest_phase'):
                report += f"- **Slowest Phase**: {perf['slowest_phase']}\n"
        
        report += "\n## [RECOMMENDATIONS]\n"
        if self.validation_results["recommendations"]:
            for rec in self.validation_results["recommendations"]:
                report += f"\n### [{rec['priority']}] {rec['action']}\n"
                if 'command' in rec:
                    report += f"```bash\n{rec['command']}\n```\n"
        else:
            report += "No specific recommendations - workflow executed successfully!\n"
        
        report += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # Save report
        report_path.write_text(report, encoding='utf-8')
        self.validation_results["report_path"] = str(report_path)
        
        # Print summary to console
        self._print_summary()
        
        return report_path
    
    def _get_health_bar(self, score):
        """Generate visual health bar"""
        filled = int(score / 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        
        if score >= 90:
            color = "🟢"
        elif score >= 70:
            color = "🟡"
        elif score >= 50:
            color = "🟠"
        else:
            color = "🔴"
        
        return f"{color} [{bar}] {score}%"
    
    def _print_summary(self):
        """Print summary to console"""
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        
        # Health score with visual
        print(f"\nHealth Score: {self._get_health_bar(self.validation_results['health_score'])}")
        print(f"Status: {self.validation_results['overall_status']}")
        
        # Quick stats
        print("\nQuick Stats:")
        print(f"  Files Generated: {self.validation_results['metrics'].get('files_generated', 0)}")
        print(f"  Issues Found: {len(self.validation_results['issues'])}")
        print(f"  Warnings: {len(self.validation_results['warnings'])}")
        
        perf = self.validation_results['metrics'].get('performance', {})
        if perf.get('total_duration'):
            print(f"  Execution Time: {perf['total_duration']:.1f}s ({perf.get('performance_grade', 'N/A')})")
        
        # Top recommendations
        if self.validation_results["recommendations"]:
            print("\nTop Recommendations:")
            for rec in self.validation_results["recommendations"][:3]:
                print(f"  [{rec['priority']}] {rec['action']}")
                if 'command' in rec:
                    print(f"    → {rec['command']}")
        
        # Report location
        if "report_path" in self.validation_results:
            print(f"\nDetailed report saved to:")
            print(f"  {self.validation_results['report_path']}")
        
        print("\n" + "=" * 80)


def validate_latest_workflow(spec_name: str):
    """Convenience function to validate the latest workflow for a spec"""
    validator = WorkflowValidator(spec_name=spec_name)
    return validator.validate_workflow()


def validate_workflow_by_id(workflow_id: str, spec_name: str = None):
    """Validate a specific workflow by ID"""
    validator = WorkflowValidator(workflow_id=workflow_id, spec_name=spec_name)
    return validator.validate_workflow()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python workflow_validator.py <spec-name> [workflow-id]")
        print("Example: python workflow_validator.py user-authentication")
        sys.exit(1)
    
    spec_name = sys.argv[1]
    workflow_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if workflow_id:
        results = validate_workflow_by_id(workflow_id, spec_name)
    else:
        results = validate_latest_workflow(spec_name)
    
    # Return exit code based on health score
    if results["health_score"] >= 70:
        sys.exit(0)
    else:
        sys.exit(1)