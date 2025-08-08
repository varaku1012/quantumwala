#!/usr/bin/env python3
"""
Simple script to execute real workflow using claude code directly
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def main():
    """Execute real workflow"""
    spec_name = "user-auth"
    description = "User authentication system with secure login, 2FA support, and password recovery"
    
    print(f"""
==================================================================
      EXECUTING REAL WORKFLOW WITH CLAUDE CODE               
==================================================================
 Spec: {spec_name}
 Description: {description}
 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================================
    """)
    
    # Execute the dev-workflow command directly
    command = f'claude-code "/dev-workflow \\"{description}\\""'
    
    print(f"\n[EXECUTING] {command}")
    print("\nThis will use the chief-product-manager agent to orchestrate the entire workflow.")
    print("Please wait while the workflow executes...\n")
    
    start_time = time.time()
    
    try:
        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        print(f"\n[COMPLETE] Workflow execution finished in {duration:.2f}s")
        print(f"Exit code: {result.returncode}")
        
        if result.stdout:
            print("\n[OUTPUT]")
            print(result.stdout)
        
        if result.stderr:
            print("\n[ERRORS]")
            print(result.stderr)
            
        # Check if spec was created
        spec_dir = Path.cwd() / '.claude' / 'specs' / spec_name
        if spec_dir.exists():
            print(f"\n[SUCCESS] Spec created at: {spec_dir}")
            
            # List created files
            files = list(spec_dir.rglob('*'))
            if files:
                print(f"\n[CREATED FILES]")
                for f in files:
                    if f.is_file():
                        print(f"  - {f.relative_to(spec_dir)}")
        else:
            print(f"\n[WARNING] Spec directory not found at expected location")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to execute workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()