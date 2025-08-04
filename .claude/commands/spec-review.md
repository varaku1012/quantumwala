Review implementation for quality.

Arguments:
- task-id: Task identifier to review

Process:
1. Use qa-engineer to:
   - Run existing tests
   - Create additional test cases
   - Check coverage
   - Perform integration testing
2. Use code-reviewer to:
   - Review code quality
   - Check best practices
   - Identify security issues
   - Suggest improvements
3. Generate review report

Output:
- Review report in .claude/specs/{spec-name}/reviews/task-{id}-review.md
- Updated test results
- Coverage reports

Usage: /spec-review [task-id]