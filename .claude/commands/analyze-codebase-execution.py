#!/usr/bin/env python3
"""
Execution script for the analyze-codebase command
Integrates with the codebase-analyst agent and generates comprehensive documentation

---
name: analyze-codebase-execution
version: 1.0.0
created: 2025-08-04
updated: 2025-08-04
changelog:
  - "1.0.0: Initial command execution script"
dependencies:
  - codebase_analyzer>=1.0.0
  - codebase-analyst>=1.0.0
---
"""

import sys
import argparse
from pathlib import Path

# Add the scripts directory to the path to import codebase_analyzer
current_dir = Path(__file__).parent
scripts_dir = current_dir.parent / 'scripts'
sys.path.append(str(scripts_dir))

try:
    from codebase_analyzer import CodebaseAnalyzer
except ImportError:
    print("Error: codebase_analyzer module not found")
    sys.exit(1)

def main():
    """Main execution function for analyze-codebase command"""
    parser = argparse.ArgumentParser(description='Analyze codebase and generate steering documents')
    parser.add_argument('repository_path', help='Path to the repository to analyze')
    parser.add_argument('--deep', action='store_true', help='Perform deep analysis including git history')
    parser.add_argument('--output', help='Output directory for generated documents')
    parser.add_argument('--format', choices=['md', 'json', 'yaml'], default='md', help='Output format')
    parser.add_argument('--focus', choices=['product', 'tech', 'architecture'], help='Focus analysis on specific areas')
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repository_path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path '{repo_path}' does not exist")
        sys.exit(1)
    
    print(f"🔍 Starting codebase analysis with codebase-analyst agent")
    print(f"📂 Repository: {repo_path}")
    print(f"⚙️  Deep analysis: {'Yes' if args.deep else 'No'}")
    print(f"🎯 Focus: {args.focus or 'All areas'}")
    print()
    
    try:
        # Initialize the analyzer
        analyzer = CodebaseAnalyzer(repo_path)
        
        # Perform analysis
        print("🚀 Phase 1: Repository Analysis")
        analysis_data = analyzer.analyze(deep=args.deep)
        
        # Generate steering documents
        print("📝 Phase 2: Generating Steering Documents")
        analyzer.generate_steering_documents()
        
        # Export analysis data if requested
        if args.format == 'json':
            print("💾 Phase 3: Exporting Analysis Data")
            export_file = analyzer.export_analysis()
            print(f"   └── Exported to: {export_file}")
        
        # Display summary
        print("\n✅ Analysis Complete!")
        print(f"📊 Summary:")
        print(f"   ├── Files analyzed: {analysis_data['metadata']['total_files']}")
        print(f"   ├── Lines of code: {analysis_data['metadata']['total_lines']}")
        print(f"   ├── Technologies detected: {len(analysis_data.get('technology_stack', {}))}")
        print(f"   ├── Features identified: {len(analysis_data.get('features', []))}")
        print(f"   └── API endpoints found: {len(analysis_data.get('apis', []))}")
        
        print(f"\n📋 Generated Documents:")
        steering_dir = analyzer.claude_dir / 'steering'
        for doc in ['product.md', 'tech.md', 'structure.md']:
            doc_path = steering_dir / doc
            if doc_path.exists():
                print(f"   ├── {doc_path}")
            else:
                print(f"   ├── {doc} (not generated)")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review generated steering documents in: {steering_dir}")
        print(f"   2. Validate and customize the product context")
        print(f"   3. Run /steering-setup to initialize the multi-agent system")
        print(f"   4. Create your first specification with /spec-create")
        
        # Integration with multi-agent workflow
        print(f"\n🤖 Multi-Agent Integration:")
        print(f"   • Use chief-product-manager for strategic product refinement")
        print(f"   • Use business-analyst for detailed requirements extraction")
        print(f"   • Use architect for technical architecture validation")
        print(f"   • Monitor progress with /dashboard enhanced")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print(f"Please check the repository path and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()