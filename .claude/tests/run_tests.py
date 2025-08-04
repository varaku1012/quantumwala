#!/usr/bin/env python3
"""
Test runner for Claude Code multi-agent system
Runs all tests and generates comprehensive report
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

def run_test_suite(test_name, test_file):
    """Run a single test suite and capture results"""
    print(f"\nRunning {test_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        return {
            'name': test_name,
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        return {
            'name': test_name,
            'success': False,
            'output': '',
            'error': str(e)
        }

def generate_test_report(results):
    """Generate comprehensive test report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    
    report = f"""# Claude Code Multi-Agent System - Test Report

Generated: {timestamp}

## Summary
- Total Test Suites: {total_tests}
- Passed: {passed_tests}
- Failed: {total_tests - passed_tests}
- Success Rate: {(passed_tests/total_tests*100):.1f}%

## Test Results
"""
    
    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        report += f"\n### {result['name']} {status}\n"
        
        if result['success']:
            # Extract key info from output
            if "tests run" in result['output'].lower():
                report += "- Tests completed successfully\n"
        else:
            report += f"- Error: {result['error'][:200]}...\n" if result['error'] else "- Test failed\n"
    
    report += "\n## Recommendations\n"
    
    if passed_tests < total_tests:
        report += "- Fix failing tests before proceeding\n"
        report += "- Check test dependencies and imports\n"
    else:
        report += "- All tests passing - ready for production\n"
        report += "- Consider adding more test coverage\n"
    
    return report

def main():
    """Main test runner"""
    test_dir = Path(__file__).parent
    
    # Define test suites
    test_suites = [
        ('Steering Context Tests', 'test_steering_context.py'),
        # Add more test files as they're created
        # ('Dashboard Tests', 'test_dashboard.py'),
        # ('Log Management Tests', 'test_log_management.py'),
    ]
    
    results = []
    
    print("Claude Code Test Runner")
    print("=" * 50)
    
    for test_name, test_file in test_suites:
        test_path = test_dir / test_file
        if test_path.exists():
            result = run_test_suite(test_name, str(test_path))
            results.append(result)
        else:
            print(f"Skipping {test_name} - file not found")
    
    # Generate report
    report = generate_test_report(results)
    
    # Save report
    report_path = test_dir.parent / 'logs' / 'reports' / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"\nTest report saved to: {report_path}")
    print("\nSummary:")
    print(report.split("## Recommendations")[0])
    
    # Exit with appropriate code
    all_passed = all(r['success'] for r in results)
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()