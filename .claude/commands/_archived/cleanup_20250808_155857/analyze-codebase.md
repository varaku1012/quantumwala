---
name: analyze-codebase
version: 1.0.0
created: 2025-08-04
updated: 2025-08-04
changelog:
  - "1.0.0: Initial codebase analysis command"
dependencies:
  - codebase-analyst>=1.0.0
---

# Analyze Codebase Command

Reverse-engineer comprehensive steering context documents and specifications from existing codebases

## Usage
```
/analyze-codebase [repository-path] [options]
```

Options:
- `--deep` - Perform deep analysis including git history and performance profiling
- `--output [dir]` - Specify output directory for generated documents
- `--format [md|json|yaml]` - Output format for documentation
- `--focus [product|tech|architecture]` - Focus analysis on specific areas

## Execution
```python
import subprocess
import sys
from pathlib import Path

# Find project root and execution script
current = Path.cwd()
while current != current.parent:
    if (current / '.claude').exists():
        break
    current = current.parent

execution_script = current / '.claude' / 'commands' / 'analyze-codebase-execution.py'

if execution_script.exists():
    # Get command arguments from context
    args = context.get('args', '').strip().split()
    
    if not args:
        print("Usage: /analyze-codebase <repository-path> [options]")
        print("Example: /analyze-codebase ./my-project --deep")
        return
    
    # Execute the analysis
    cmd = [sys.executable, str(execution_script)] + args
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode == 0:
        print("\n🎉 Codebase analysis completed successfully!")
        print("Review the generated steering documents and customize as needed.")
    else:
        print("❌ Analysis failed. Check the error messages above.")
else:
    print("Error: analyze-codebase-execution.py script not found")
```

## Examples

### Basic Codebase Analysis
```
/analyze-codebase ./my-project
```
Analyzes the codebase and generates:
- Product steering context
- Technology steering context  
- Architecture documentation
- Feature specifications

### Deep Analysis with Custom Output
```
/analyze-codebase ./e-commerce-app --deep --output ./docs --format md
```

### Focused Analysis
```
/analyze-codebase ./api-service --focus architecture
```

## Analysis Process

### Phase 1: Repository Reconnaissance
1. **Structure Analysis**: Map directory structure and module organization
2. **Technology Detection**: Identify languages, frameworks, dependencies
3. **Documentation Review**: Parse existing README, comments, docs
4. **Git History**: Analyze commit patterns and evolution timeline

### Phase 2: Architecture Deep Dive
1. **Component Mapping**: Identify system components and boundaries  
2. **Data Flow Analysis**: Trace data movement and storage patterns
3. **API Discovery**: Document all external interfaces and endpoints
4. **Integration Analysis**: Map third-party services and dependencies

### Phase 3: Business Logic Extraction
1. **Feature Inventory**: Catalog all implemented capabilities
2. **User Journey Mapping**: Trace user workflows through code
3. **Business Rules**: Extract validation logic and constraints
4. **Value Proposition**: Understand problem-solution fit

### Phase 4: Documentation Generation
1. **Steering Contexts**: Generate product, tech, and structure docs
2. **Specifications**: Create detailed feature and API specs
3. **Architecture Diagrams**: Visual system representations
4. **Gap Analysis**: Identify missing features and improvements

## Generated Outputs

### Steering Context Documents
```
.claude/steering/
├── product.md           # Product vision, users, features, metrics
├── tech.md             # Technology stack, architecture, standards  
├── structure.md        # Code organization, patterns, workflows
└── README.md           # Overview and usage guide
```

### Technical Specifications
```
.claude/specs/
├── architecture/       # System architecture documentation
├── apis/              # API specifications and documentation
├── features/          # Individual feature specifications
└── integrations/      # External service integrations
```

### Analysis Reports
```
.claude/analysis/
├── codebase-summary.md    # Executive summary of findings
├── feature-matrix.md      # Complete feature inventory
├── tech-stack-analysis.md # Technology assessment
├── gap-analysis.md        # Missing features and recommendations
└── performance-profile.md # Performance and scalability analysis
```

## Supported Project Types

### Web Applications
- React, Vue, Angular frontends
- Node.js, Python, Ruby, Java backends
- REST APIs, GraphQL, WebSocket services
- Database integrations (SQL, NoSQL)

### Mobile Applications
- React Native, Flutter cross-platform
- iOS (Swift, Objective-C)
- Android (Kotlin, Java)
- Hybrid apps (Cordova, Ionic)

### E-commerce Platforms
- Shopping cart and checkout systems
- Payment gateway integrations
- Inventory management systems
- Customer relationship management

### SaaS Applications
- Multi-tenant architectures
- User authentication and authorization
- Subscription and billing systems
- API marketplaces and integrations

### AI/ML Systems
- Data processing pipelines
- Model training and inference
- Feature engineering workflows
- ML model serving infrastructure

## Analysis Capabilities

### Code Analysis
- **Static Analysis**: Pattern recognition, dependency mapping, quality assessment
- **Dynamic Analysis**: Runtime behavior, performance profiling, user flow tracing
- **Security Analysis**: Vulnerability detection, access control review
- **Quality Metrics**: Code complexity, test coverage, maintainability scores

### Business Intelligence
- **Market Positioning**: Infer target market from feature analysis
- **User Personas**: Derive user types from UI/UX patterns
- **Revenue Models**: Understand monetization from payment code
- **Competitive Analysis**: Compare features with market standards

### Architecture Assessment
- **Scalability Review**: Identify performance bottlenecks and scaling limitations
- **Integration Mapping**: Document all external service dependencies
- **Data Architecture**: Database schema, data flow, storage patterns
- **Security Model**: Authentication, authorization, data protection

## Integration with Multi-Agent Workflow

The codebase analysis integrates with other agents:

1. **Codebase Analyst** → **Chief Product Manager**: Strategic product insights
2. **Codebase Analyst** → **Business Analyst**: Requirements and user stories
3. **Codebase Analyst** → **Architect**: Technical architecture validation
4. **Codebase Analyst** → **Developer**: Implementation recommendations

## Quality Assurance

All analysis outputs include:
- **Confidence Levels**: Mark inferences vs confirmed facts
- **Source References**: Link findings to specific code locations
- **Validation Checks**: Cross-reference findings across multiple sources
- **Review Notes**: Areas requiring human validation

## Best Practices

### Preparation
1. Ensure codebase is complete and up-to-date
2. Include access to any existing documentation
3. Provide context about business domain and users
4. Share any architectural decisions or constraints

### Review Process
1. Validate generated steering documents against actual product
2. Verify technical specifications with development team
3. Cross-check business logic extraction with product managers
4. Update and refine generated documentation as needed

## Advanced Features

### Custom Analysis Rules
Create custom analysis patterns for domain-specific logic:
```yaml
# .claude/analysis-rules.yaml
patterns:
  payment_processing:
    files: ["**/payment/**", "**/billing/**"]
    extract: ["gateway_configs", "transaction_flows"]
  user_authentication:
    files: ["**/auth/**", "**/user/**"]
    extract: ["login_flows", "permission_models"]
```

### Integration with Version Control
Analyze codebase evolution and feature development patterns:
- Commit message analysis for feature identification
- Author activity patterns for team structure insights
- Code churn analysis for stability assessment
- Release pattern analysis for development velocity

## Output Validation

Generated documents include validation metadata:
```yaml
---
analysis_metadata:
  confidence_level: high|medium|low
  source_files_analyzed: 1247
  last_updated: 2025-08-04
  validation_required:
    - business_logic_accuracy
    - user_persona_validation
    - technical_architecture_review
---
```

## Continuous Analysis

Set up automated analysis for ongoing documentation maintenance:
- Git hooks for incremental analysis
- CI/CD integration for documentation updates
- Scheduled full re-analysis for comprehensive updates
- Change detection for architectural modifications