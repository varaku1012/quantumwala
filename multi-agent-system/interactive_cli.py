"""
Interactive CLI for Quantumwala Multi-Agent System
Provides an easy-to-use interface for running agents
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import sys
from datetime import datetime

try:
    from orchestrator import ClaudeCodeOrchestrator
    from templates.agent_templates import AGENT_TEMPLATES, get_agent_chain
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run install.bat first")
    sys.exit(1)


class InteractiveCLI:
    """Interactive command-line interface for the multi-agent system"""
    
    def __init__(self):
        self.orchestrator = None
        self.current_project = None
        self.history = []
        
    def print_header(self):
        """Print CLI header"""
        print("\n" + "="*60)
        print("   Quantumwala Multi-Agent System - Interactive Mode")
        print("   With Unified Documentation Support")
        print("="*60)
        
    def print_menu(self):
        """Print main menu"""
        print("\n📋 Main Menu:")
        print("1. 🚀 Quick Start (Build Something)")
        print("2. 👤 Run Single Agent")
        print("3. ⚡ Run Parallel Agents")
        print("4. 🔄 Run Agent Chain")
        print("5. 📊 View Metrics")
        print("6. 📚 Test Documentation Server")
        print("7. 🛠️ Configure Settings")
        print("8. 📝 View History")
        print("9. ❌ Exit")
        
    async def quick_start(self):
        """Quick start wizard for common projects"""
        print("\n🚀 Quick Start - What would you like to build?")
        print("1. 🌐 Web Application")
        print("2. 📱 REST API")
        print("3. 🔧 Microservice")
        print("4. 📊 Dashboard")
        print("5. 🤖 Automation Script")
        print("6. ✨ Custom Project")
        
        choice = input("\nSelect project type (1-6): ").strip()
        
        project_templates = {
            "1": ("web", "Modern web application with React and Node.js"),
            "2": ("api", "RESTful API with authentication and database"),
            "3": ("microservice", "Microservice with Docker and Kubernetes"),
            "4": ("dashboard", "Analytics dashboard with real-time data"),
            "5": ("automation", "Python automation script with scheduling"),
            "6": ("custom", None)
        }
        
        if choice not in project_templates:
            print("❌ Invalid choice")
            return
            
        project_type, default_desc = project_templates[choice]
        
        if project_type == "custom":
            description = input("\nDescribe your project: ").strip()
            project_type = "web"  # Default to web for custom
        else:
            print(f"\n📝 Default: {default_desc}")
            custom = input("Press Enter to use default or type custom description: ").strip()
            description = custom if custom else default_desc
            
        print(f"\n🏗️ Building: {description}")
        print("⏳ Starting multi-agent workflow...\n")
        
        # Get agent chain for project type
        agent_chain = get_agent_chain(project_type)
        
        # Initialize orchestrator
        if not self.orchestrator:
            self.orchestrator = ClaudeCodeOrchestrator(".", enable_docs=True)
            
        results = {}
        
        # Run agent chain
        for i, agent_type in enumerate(agent_chain, 1):
            print(f"\n[{i}/{len(agent_chain)}] Running {agent_type.replace('_', ' ').title()} Agent...")
            
            # Prepare input based on previous results
            input_data = self._prepare_agent_input(agent_type, results, description)
            
            try:
                result = await self.orchestrator.run_agent(
                    agent_type=agent_type,
                    task=f"Process for: {description}",
                    input_data=input_data,
                    use_docs=True
                )
                
                results[agent_type] = result
                
                if result.get('validation'):
                    score = result['validation'].get('score', 'N/A')
                    print(f"   ✅ Completed - Validation Score: {score}/100")
                else:
                    print(f"   ✅ Completed")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[agent_type] = {"status": "error", "error": str(e)}
                
        # Summary
        print("\n" + "="*50)
        print("📊 Workflow Complete!")
        print("="*50)
        
        successful = sum(1 for r in results.values() if r.get('status') != 'error')
        print(f"✅ Successful Agents: {successful}/{len(agent_chain)}")
        
        # Save to history
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "project": description,
            "results": results
        })
        
    def _prepare_agent_input(self, agent_type: str, previous_results: Dict, 
                            description: str) -> Dict:
        """Prepare input data for agent based on previous results"""
        input_data = {"project_description": description}
        
        # Add relevant previous results
        if agent_type == "business_analyst" and "product_manager" in previous_results:
            input_data["vision"] = previous_results["product_manager"].get("output", {})
            
        elif agent_type == "architect" and "business_analyst" in previous_results:
            input_data["requirements"] = previous_results["business_analyst"].get("output", {})
            
        elif agent_type == "developer":
            if "architect" in previous_results:
                input_data["architecture"] = previous_results["architect"].get("output", {})
            if "business_analyst" in previous_results:
                input_data["requirements"] = previous_results["business_analyst"].get("output", {})
                
        elif agent_type == "qa_engineer" and "developer" in previous_results:
            input_data["code_base"] = previous_results["developer"].get("output", {})
            
        return input_data
        
    async def run_single_agent(self):
        """Run a single agent with custom task"""
        print("\n👤 Available Agents:")
        agents = list(AGENT_TEMPLATES.keys())
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent.replace('_', ' ').title()}")
            
        choice = input("\nSelect agent (1-{}): ".format(len(agents))).strip()
        
        try:
            agent_type = agents[int(choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
            
        task = input(f"\nEnter task for {agent_type.replace('_', ' ').title()}: ").strip()
        
        if not task:
            print("❌ Task cannot be empty")
            return
            
        print(f"\n⏳ Running {agent_type} agent...")
        
        if not self.orchestrator:
            self.orchestrator = ClaudeCodeOrchestrator(".", enable_docs=True)
            
        try:
            result = await self.orchestrator.run_agent(
                agent_type=agent_type,
                task=task,
                input_data={},
                use_docs=True
            )
            
            print("\n✅ Agent completed successfully!")
            
            if result.get('validation'):
                print(f"📊 Validation Score: {result['validation']['score']}/100")
                
                if result['validation'].get('deprecated_apis'):
                    print("\n⚠️ Deprecated APIs detected:")
                    for api in result['validation']['deprecated_apis']:
                        print(f"  - {api['api']} → Use: {api.get('alternative', 'N/A')}")
                        
                if result['validation'].get('security_issues'):
                    print("\n🔒 Security issues found:")
                    for issue in result['validation']['security_issues']:
                        print(f"  - {issue['warning']}")
                        
            # Save to history
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent_type,
                "task": task,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
    async def run_parallel_agents(self):
        """Run multiple agents in parallel"""
        print("\n⚡ Parallel Agent Execution")
        print("Enter tasks for multiple agents (empty line to finish):")
        
        tasks = []
        agents = list(AGENT_TEMPLATES.keys())
        
        while True:
            print(f"\nTask {len(tasks) + 1}:")
            print("Available agents:", ", ".join(agents))
            
            agent = input("Agent type: ").strip()
            if not agent:
                break
                
            if agent not in agents:
                print("❌ Invalid agent type")
                continue
                
            task_desc = input("Task description: ").strip()
            if not task_desc:
                print("❌ Task cannot be empty")
                continue
                
            tasks.append((agent, task_desc, {}))
            
        if not tasks:
            print("❌ No tasks defined")
            return
            
        print(f"\n⏳ Running {len(tasks)} agents in parallel...")
        
        if not self.orchestrator:
            self.orchestrator = ClaudeCodeOrchestrator(".", enable_docs=True)
            
        try:
            results = await self.orchestrator.run_parallel_agents(tasks)
            
            print("\n✅ Parallel execution complete!")
            print("\nResults:")
            for i, result in enumerate(results, 1):
                agent = tasks[i-1][0]
                status = result.get('status', 'unknown')
                score = result.get('validation', {}).get('score', 'N/A') if result.get('validation') else 'N/A'
                print(f"  {i}. {agent}: {status} (Score: {score})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    async def test_documentation_server(self):
        """Test documentation server functionality"""
        print("\n📚 Testing Documentation Server")
        
        test_queries = [
            "React useState hook",
            "Python asyncio",
            "Express middleware",
            "PostgreSQL indexes",
            "Docker compose"
        ]
        
        from unified_doc_server import UnifiedDocumentationServer
        
        try:
            async with UnifiedDocumentationServer() as doc_server:
                print("\n✅ Documentation server initialized")
                
                for query in test_queries:
                    print(f"\n🔍 Searching: {query}")
                    results = await doc_server.query(query)
                    
                    if results:
                        print(f"  Found {len(results)} results")
                        top_result = results[0]
                        print(f"  Top result: {top_result.title} ({top_result.source})")
                        print(f"  Relevance: {top_result.relevance_score:.1f}")
                    else:
                        print("  No results found")
                        
                # Test code validation
                print("\n🔍 Testing Code Validation:")
                sample_code = """
                const data = localStorage.getItem('data');
                document.write(userInput);
                eval(someString);
                """
                
                validation = await doc_server.validate_code(sample_code, "javascript")
                
                if validation['deprecated_apis']:
                    print(f"  ⚠️ Deprecated APIs: {len(validation['deprecated_apis'])}")
                    
                if validation['security_issues']:
                    print(f"  🔒 Security issues: {len(validation['security_issues'])}")
                    
                print(f"\n✅ Documentation server test complete!")
                
        except Exception as e:
            print(f"❌ Error testing documentation server: {e}")
            
    def view_metrics(self):
        """View agent performance metrics"""
        if not self.orchestrator:
            print("❌ No metrics available. Run some agents first.")
            return
            
        print(self.orchestrator.get_metrics_report())
        
    def view_history(self):
        """View command history"""
        if not self.history:
            print("📝 No history available yet.")
            return
            
        print("\n📝 Command History:")
        for i, entry in enumerate(self.history[-10:], 1):  # Last 10 entries
            timestamp = entry['timestamp']
            if 'agent' in entry:
                print(f"{i}. [{timestamp}] {entry['agent']}: {entry['task'][:50]}...")
            else:
                print(f"{i}. [{timestamp}] Project: {entry.get('project', 'Unknown')[:50]}...")
                
    async def run(self):
        """Main CLI loop"""
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                await self.quick_start()
            elif choice == "2":
                await self.run_single_agent()
            elif choice == "3":
                await self.run_parallel_agents()
            elif choice == "4":
                print("🔄 Use Quick Start for agent chains")
                await self.quick_start()
            elif choice == "5":
                self.view_metrics()
            elif choice == "6":
                await self.test_documentation_server()
            elif choice == "7":
                print("🛠️ Edit configs/documentation-config.yaml to configure")
            elif choice == "8":
                self.view_history()
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        # Save history before exit
        if self.history:
            history_file = Path("logs/cli_history.json")
            history_file.parent.mkdir(exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
                

def main():
    """Entry point"""
    cli = InteractiveCLI()
    
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        

if __name__ == "__main__":
    main()
