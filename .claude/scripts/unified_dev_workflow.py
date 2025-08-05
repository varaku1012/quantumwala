#!/usr/bin/env python3
"""
Unified developer workflow
Simple interface that uses chief-product-manager agent internally
"""

import re
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from developer_errors import DeveloperError, DeveloperSuggestion, developer_friendly
    from dev_environment_validator import DevEnvironmentValidator
    from real_executor import RealClaudeExecutor, ExecutionResult
except ImportError as e:
    print(f"❌ Missing required modules. Run: python .claude/scripts/dev_environment_validator.py")
    sys.exit(1)

@dataclass
class WorkflowPhase:
    """Represents a phase in the development workflow"""
    name: str
    description: str
    agents: List[str]
    commands: List[str]
    estimated_minutes: int

@dataclass
class AgentSelection:
    """Represents selected agents for a workflow"""
    primary_agents: List[str]
    supporting_agents: List[str]
    reasoning: str

class UnifiedDevWorkflow:
    """Unified developer workflow that uses chief-product-manager internally"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or self._find_project_root()
        self.claude_dir = self.project_root / '.claude'
        self.executor = RealClaudeExecutor(self.project_root)
        
        # Agent capability mapping for context
        self.agent_keywords = {
            'api': ['architect', 'api-integration-specialist', 'developer'],
            'rest': ['architect', 'api-integration-specialist', 'developer'],
            'graphql': ['architect', 'api-integration-specialist', 'developer'],
            'ui': ['uiux-designer', 'developer', 'qa-engineer'],
            'interface': ['uiux-designer', 'developer', 'qa-engineer'],
            'component': ['uiux-designer', 'developer', 'qa-engineer'],
            'frontend': ['uiux-designer', 'developer', 'performance-optimizer'],
            'authentication': ['security-engineer', 'developer', 'qa-engineer'],
            'login': ['security-engineer', 'developer', 'qa-engineer'],
            'security': ['security-engineer', 'developer', 'qa-engineer'],
            'database': ['data-engineer', 'developer', 'qa-engineer'],
            'data': ['data-engineer', 'developer', 'architect'],
            'storage': ['data-engineer', 'developer', 'architect'],
            'performance': ['performance-optimizer', 'developer', 'architect'],
            'optimization': ['performance-optimizer', 'developer', 'architect'],
            'deployment': ['devops-engineer', 'developer', 'security-engineer'],
            'infrastructure': ['devops-engineer', 'architect', 'security-engineer'],
            'testing': ['qa-engineer', 'developer', 'security-engineer'],
            'backend': ['developer', 'architect', 'data-engineer'],
            'machine learning': ['genai-engineer', 'data-engineer', 'developer'],
            'ai': ['genai-engineer', 'data-engineer', 'developer'],
            'integration': ['api-integration-specialist', 'developer', 'qa-engineer']
        }
        
        # Workflow phases (for planning display only)
        self.display_phases = [
            'Strategic Analysis & Planning',
            'Agent Orchestration & Requirements',
            'Design & Architecture', 
            'Task Generation & Planning',
            'Implementation Orchestration',
            'Quality Assurance & Deployment'
        ]
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for .claude directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.claude').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    @developer_friendly
    def analyze_description(self, description: str) -> AgentSelection:
        """Analyze description and select appropriate agents"""
        description_lower = description.lower()
        
        # Find matching keywords
        matched_agents = set()
        matched_keywords = []
        
        for keyword, agents in self.agent_keywords.items():
            if keyword in description_lower:
                matched_agents.update(agents)
                matched_keywords.append(keyword)
        
        # If no specific matches, use general development agents
        if not matched_agents:
            matched_agents = {'business-analyst', 'architect', 'developer', 'qa-engineer'}
            reasoning = "General development workflow (no specific keywords detected)"
        else:
            reasoning = f"Detected keywords: {', '.join(matched_keywords)}"
        
        # Separate primary and supporting agents
        primary_agents = list(matched_agents)
        supporting_agents = ['code-reviewer']  # Always include code review
        
        # Add security for sensitive features
        security_keywords = ['auth', 'login', 'password', 'security', 'payment', 'user']
        if any(keyword in description_lower for keyword in security_keywords):
            if 'security-engineer' not in primary_agents:
                supporting_agents.append('security-engineer')
        
        return AgentSelection(
            primary_agents=primary_agents,
            supporting_agents=supporting_agents,
            reasoning=reasoning
        )
    
    def generate_project_name(self, description: str) -> str:
        """Generate a project name from description"""
        # Extract key words and create kebab-case name
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Remove common words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'with', 'for', 'to', 'from', 'by', 'at', 'in', 'on'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take first 3-4 meaningful words
        project_words = meaningful_words[:4] if len(meaningful_words) >= 4 else meaningful_words
        
        if not project_words:
            # Fallback if no meaningful words found
            project_words = ['custom', 'feature']
        
        return '-'.join(project_words)
    
    def prepare_execution_context(self, description: str, agents: AgentSelection, mode: str = 'quick') -> Dict:
        """Prepare context for chief-product-manager execution"""
        return {
            'user_description': description,
            'execution_mode': mode,
            'developer_friendly': True,
            'suggested_agents': {
                'primary': agents.primary_agents,
                'supporting': agents.supporting_agents,
                'reasoning': agents.reasoning
            },
            'agent_selection_keywords': list(set([keyword for keyword in self.agent_keywords.keys() if keyword in description.lower()])),
            'workflow_preferences': {
                'auto_progression': True,
                'parallel_execution': True,
                'developer_output': True,
                'detailed_progress': mode in ['comprehensive', 'learning'],
                'learning_mode': mode == 'learning'
            },
            'project_context': {
                'project_root': str(self.project_root),
                'claude_dir': str(self.claude_dir)
            }
        }
    
    def print_workflow_plan(self, project_name: str, description: str, agents: AgentSelection, mode: str):
        """Print the planned workflow for user review"""
        estimated_time = {
            'quick': 45,
            'comprehensive': 90, 
            'learning': 120
        }.get(mode, 45)
        
        print(f"\n🚀 DEVELOPMENT WORKFLOW PLAN")
        print("=" * 50)
        print(f"📋 Project: {project_name}")
        print(f"📝 Description: {description}")
        print(f"⏱️  Estimated time: {estimated_time} minutes")
        print(f"🤖 Agent selection: {agents.reasoning}")
        print(f"🎯 Execution: chief-product-manager (autonomous workflow)")
        
        print(f"\n👥 AGENTS TO BE USED:")
        print(f"   Primary: {', '.join(agents.primary_agents)}")
        if agents.supporting_agents:
            print(f"   Supporting: {', '.join(agents.supporting_agents)}")
        
        print(f"\n📈 WORKFLOW PHASES (Automated):")
        for i, phase in enumerate(self.display_phases, 1):
            print(f"   {i}. {phase}")
        
        print(f"\n🎯 Ready to start? The chief-product-manager will:")
        print(f"   ✅ Execute the complete workflow autonomously")
        print(f"   ✅ Coordinate all agents automatically")
        print(f"   ✅ Progress through phases without stopping")
        print(f"   ✅ Provide developer-friendly output")
        print(f"   ✅ Handle parallel execution and optimization")
    
    def check_prerequisites(self) -> List[str]:
        """Check if environment is ready for workflow execution"""
        issues = []
        
        # Run basic environment validation
        try:
            validator = DevEnvironmentValidator(self.project_root)
            validator.run_all_validations()
            
            errors = [issue for issue in validator.issues if issue.level == 'error']
            if errors:
                issues.extend([f"{issue.component}: {issue.message}" for issue in errors])
                
        except Exception as e:
            issues.append(f"Environment validation failed: {str(e)}")
        
        return issues
    
    async def execute_with_chief_product_manager(self, description: str, context: Dict, mode: str = 'quick', timeout: int = 3600) -> ExecutionResult:
        """Execute workflow using chief-product-manager agent"""
        print(f"\n🎯 Delegating to chief-product-manager agent...")
        print(f"📋 I'll handle the complexity - you focus on building!")
        
        # Construct the command for chief-product-manager
        task_description = f'Execute complete development workflow for "{description}" in {mode} mode with developer-friendly output and progress updates'
        
        try:
            # Execute using chief-product-manager agent
            result = await self.executor.execute_agent_task(
                agent_name='chief-product-manager',
                task_description=task_description,
                context=context,
                timeout=timeout
            )
            
            return result
            
        except Exception as e:
            print(f"\n❌ Workflow execution failed: {str(e)}")
            return ExecutionResult(
                success=False,
                error=f"Chief-product-manager execution failed: {str(e)}",
                command=task_description,
                agent_used='chief-product-manager'
            )
    
    async def execute_workflow(self, description: str, mode: str = 'quick', dry_run: bool = False) -> bool:
        """Execute the complete development workflow using chief-product-manager"""
        print(f"🚀 Starting development workflow...")
        print(f"📋 Using chief-product-manager for autonomous execution!")
        
        # Generate project name
        project_name = self.generate_project_name(description)
        
        # Analyze description and select agents
        agents = self.analyze_description(description)
        
        # Prepare execution context
        context = self.prepare_execution_context(description, agents, mode)
        
        # Show plan
        self.print_workflow_plan(project_name, description, agents, mode)
        
        if dry_run:
            print(f"\n🔍 DRY RUN - No actual execution performed")
            print(f"\nWould execute with chief-product-manager agent:")
            print(f"   Task: Execute complete development workflow")
            print(f"   Description: {description}")
            print(f"   Mode: {mode}")
            print(f"   Context: {len(context)} configuration items")
            return True
        
        # Check prerequisites
        print(f"\n🔍 Checking prerequisites...")
        issues = self.check_prerequisites()
        if issues:
            print(f"\n❌ Prerequisites not met:")
            for issue in issues:
                print(f"   • {issue}")
            print(f"\n💡 Fix these issues first:")
            print(f"   Command: python .claude/scripts/dev_environment_validator.py")
            return False
        
        print(f"✅ Prerequisites check passed")
        
        # Confirm execution
        if mode != 'quick':
            response = input(f"\n❓ Proceed with workflow execution? (y/N): ")
            if response.lower() != 'y':
                print(f"⏹️  Workflow cancelled by user")
                return False
        
        # Execute workflow with chief-product-manager
        print(f"\n🔄 EXECUTING WORKFLOW WITH CHIEF-PRODUCT-MANAGER")
        print("=" * 55)
        print(f"🤖 The chief-product-manager will now take over and execute the complete workflow autonomously.")
        print(f"📋 You'll see progress updates throughout the process.")
        
        timeout = {
            'quick': 1800,      # 30 minutes
            'comprehensive': 3600,  # 60 minutes  
            'learning': 5400    # 90 minutes
        }.get(mode, 1800)
        
        try:
            result = await self.execute_with_chief_product_manager(
                description, context, mode, timeout
            )
            
            if result.success:
                print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                print("=" * 40)
                print(f"📁 Project: {project_name}")
                print(f"📝 Description: {description}")
                print(f"⏱️  Total time: {result.duration:.1f} minutes")
                print(f"🤖 Executed by: chief-product-manager")
                
                print(f"\n📂 Check your results:")
                print(f"   Specification: .claude/specs/{project_name}/")
                print(f"   Implementation: src/ (or your project structure)")
                print(f"   Documentation: Generated automatically")
                
                print(f"\n🚀 Next steps:")
                print(f"   1. Review the generated code and documentation")
                print(f"   2. Test the implementation")
                print(f"   3. Deploy when ready")
                
                return True
            else:
                print(f"\n❌ WORKFLOW EXECUTION FAILED")
                print("=" * 30)
                print(f"Error: {result.error}")
                print(f"\n💡 Try these solutions:")
                print(f"   1. Run environment validation")
                print(f"      Command: python .claude/scripts/dev_environment_validator.py")
                print(f"   2. Try with comprehensive mode for more context")
                print(f"      Command: /dev-workflow \"{description}\" --mode comprehensive")
                print(f"   3. Check the execution logs")
                print(f"      Location: .claude/logs/execution/")
                return False
                
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR")
            print("=" * 20)
            print(f"Error: {str(e)}")
            print(f"\n💡 Try these solutions:")
            print(f"   1. Run environment validation")
            print(f"      Command: python .claude/scripts/dev_environment_validator.py")
            print(f"   2. Enable development mode")
            print(f"      Command: /dev-mode on")
            return False

def main():
    """Main function for unified developer workflow"""
    parser = argparse.ArgumentParser(description='Unified Developer Workflow - Uses chief-product-manager internally')
    parser.add_argument('description', help='What you want to build')
    parser.add_argument('--mode', choices=['quick', 'comprehensive', 'learning'], 
                       default='quick', help='Workflow execution mode')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without executing')
    parser.add_argument('--agents', help='Comma-separated list of specific agents to use (passed as context)')
    parser.add_argument('--timeout', type=int, help='Timeout in minutes (overrides mode defaults)')
    
    args = parser.parse_args()
    
    try:
        workflow = UnifiedDevWorkflow()
        
        # Run the async workflow
        success = asyncio.run(workflow.execute_workflow(
            description=args.description,
            mode=args.mode,
            dry_run=args.dry_run
        ))
        
        sys.exit(0 if success else 1)
        
    except DeveloperError as e:
        print(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Workflow cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"\n💡 Try these solutions:")
        print(f"   1. Run environment validation")
        print(f"      Command: python .claude/scripts/dev_environment_validator.py")
        print(f"   2. Try with comprehensive mode")
        print(f"      Command: /dev-workflow \"{args.description}\" --mode comprehensive")
        print(f"   3. Check execution logs")
        print(f"      Location: .claude/logs/execution/")
        sys.exit(1)

if __name__ == "__main__":
    main()