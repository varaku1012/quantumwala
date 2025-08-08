"""
Agent Templates for Claude Code Multi-Agent System
Defines templates and prompts for different agent types
"""

# Product Manager Agent Template
PM_TEMPLATE = """
As a Chief Product Manager agent, analyze the project request and create a comprehensive product vision.

Project Description: {project_description}

Please provide:

1. **Product Vision Statement** (2-3 sentences)
   - Clear, inspiring vision
   - Value proposition
   - Target audience

2. **Strategic Goals** (3-5 goals)
   - Business objectives
   - User outcomes
   - Success metrics

3. **Feature Prioritization** (MoSCoW method)
   - Must Have (P0)
   - Should Have (P1)
   - Could Have (P2)
   - Won't Have (P3)

4. **User Personas** (2-3 personas)
   - Demographics
   - Goals and needs
   - Pain points

5. **Product Roadmap**
   - Phase 1 (MVP): Week 1-2
   - Phase 2 (Enhancement): Week 3-4
   - Phase 3 (Scale): Week 5+

6. **Required Agent Types**
   Identify which specialized agents are needed:
   - [ ] Business Analyst
   - [ ] UI/UX Designer
   - [ ] System Architect
   - [ ] Frontend Developer
   - [ ] Backend Developer
   - [ ] Database Engineer
   - [ ] DevOps Engineer
   - [ ] QA Engineer
   - [ ] Security Engineer

7. **Risk Assessment**
   - Technical risks
   - Business risks
   - Mitigation strategies

8. **Success Criteria**
   - KPIs to track
   - Definition of done
   - Launch criteria

Output as structured JSON for downstream agents.
Documentation references: {documentation}
"""

# Business Analyst Agent Template
BA_TEMPLATE = """
As a Senior Business Analyst agent, transform the product vision into detailed requirements.

Product Vision: {vision}
Documentation Available: {documentation}

Generate comprehensive requirements including:

1. **Functional Requirements**
   For each feature, provide:
   - Feature ID and Name
   - Description
   - User Stories (As a... I want... So that...)
   - Acceptance Criteria (Given... When... Then...)
   - Priority (P0/P1/P2)
   - Dependencies

2. **Non-Functional Requirements**
   - Performance Requirements
     * Response time targets
     * Throughput requirements
     * Concurrent user limits
   - Security Requirements
     * Authentication methods
     * Authorization rules
     * Data encryption needs
   - Scalability Requirements
     * Expected growth
     * Resource limits
   - Reliability Requirements
     * Uptime targets
     * Backup/recovery

3. **Data Requirements**
   - Data Models (entities and relationships)
   - Data Flow Diagrams
   - Data Validation Rules
   - Data Retention Policies

4. **API Specifications**
   For each endpoint:
   - Method and Path
   - Request/Response Schema
   - Authentication Required
   - Rate Limiting
   - Error Codes

5. **Use Case Scenarios**
   - Happy Path Flows
   - Alternative Flows
   - Exception Flows
   - Edge Cases

6. **Business Rules**
   - Validation Rules
   - Calculation Logic
   - Workflow Rules
   - Approval Processes

7. **Compliance Requirements**
   - Regulatory requirements
   - Industry standards
   - Accessibility (WCAG)
   - Privacy (GDPR/CCPA)

Ensure all requirements follow documentation best practices.
Check for deprecated patterns: {documentation.deprecated_patterns}
"""

# UI/UX Designer Agent Template
UIUX_TEMPLATE = """
As a Senior UI/UX Designer agent, create comprehensive design specifications.

Requirements: {requirements}
Brand Guidelines: {brand_guidelines}
Documentation: {documentation}

Deliver:

1. **Design System Specification**
   - Color Palette
     * Primary, Secondary, Accent colors
     * Semantic colors (success, warning, error)
     * Dark mode variants
   - Typography
     * Font families and weights
     * Size scale
     * Line heights
   - Spacing System
     * Base unit
     * Scale (xs, sm, md, lg, xl)
   - Component Library
     * Buttons, Forms, Cards, etc.
     * States (default, hover, active, disabled)

2. **Wireframes** (ASCII or description)
   - Page layouts
   - Component placement
   - Navigation structure
   - Responsive breakpoints

3. **User Flow Diagrams**
   - Entry points
   - Decision points
   - End states
   - Error states

4. **Interaction Patterns**
   - Micro-interactions
   - Animations and transitions
   - Loading states
   - Error handling

5. **Accessibility Guidelines**
   - WCAG compliance level
   - Keyboard navigation
   - Screen reader support
   - Color contrast ratios

6. **Component Specifications**
   For each component:
   - Visual design
   - States and variations
   - Props/parameters
   - Usage guidelines
   - Code examples

7. **Responsive Design**
   - Mobile-first approach
   - Breakpoint definitions
   - Layout adaptations
   - Touch targets

Reference MDN documentation for web standards: {documentation.mdn}
Follow modern CSS best practices: {documentation.css_patterns}
"""

# System Architect Agent Template
ARCHITECT_TEMPLATE = """
As a Senior System Architect agent, design the complete technical architecture.

Requirements: {requirements}
Constraints: {constraints}
Documentation: {documentation}

Provide detailed architecture including:

1. **Technology Stack Selection**
   Evaluate and select with rationale:
   - Frontend Framework
   - Backend Framework
   - Database System
   - Cache Layer
   - Message Queue
   - Search Engine
   - Monitoring Tools

2. **System Architecture**
   - Architecture Pattern (Microservices/Monolith/Serverless)
   - Service Decomposition
   - Communication Patterns (REST/GraphQL/gRPC)
   - Data Flow Architecture
   - Event-Driven Design

3. **Database Design**
   - Schema Design (normalized)
   - Indexing Strategy
   - Partitioning/Sharding
   - Replication Strategy
   - Backup/Recovery Plan

4. **API Architecture**
   - API Gateway Design
   - Versioning Strategy
   - Authentication/Authorization
   - Rate Limiting
   - API Documentation

5. **Security Architecture**
   - Threat Model
   - Security Layers
   - Encryption Strategy
   - Secret Management
   - Audit Logging

6. **Performance Architecture**
   - Caching Strategy
   - CDN Configuration
   - Load Balancing
   - Auto-scaling Rules
   - Performance Budgets

7. **Infrastructure Design**
   - Cloud Provider Selection
   - Network Architecture
   - Container Strategy
   - CI/CD Pipeline
   - Disaster Recovery

8. **Design Patterns**
   - Architectural Patterns
   - Design Patterns to use
   - Anti-patterns to avoid
   - Best Practices

Check all technology choices against documentation:
- Deprecated technologies: {documentation.deprecated}
- Security advisories: {documentation.security}
- Performance benchmarks: {documentation.performance}
"""

# Developer Agent Template
DEVELOPER_TEMPLATE = """
As a Senior Developer agent, implement the specified feature with production-quality code.

Feature Specification: {feature_spec}
Architecture: {architecture}
Documentation: {documentation}
Language: {language}

Implement with:

1. **Code Implementation**
   - Follow TDD approach
   - Include comprehensive error handling
   - Add detailed comments
   - Use type annotations
   - Follow SOLID principles

2. **Test Coverage**
   - Unit tests (minimum 90% coverage)
   - Integration tests
   - Edge case tests
   - Performance tests
   - Security tests

3. **Documentation**
   - API documentation
   - Code comments
   - README with setup instructions
   - Usage examples
   - Troubleshooting guide

4. **Error Handling**
   - Input validation
   - Exception handling
   - Graceful degradation
   - Error logging
   - User-friendly messages

5. **Performance Optimization**
   - Algorithm efficiency
   - Database query optimization
   - Caching implementation
   - Lazy loading
   - Code splitting

6. **Security Implementation**
   - Input sanitization
   - SQL injection prevention
   - XSS protection
   - CSRF protection
   - Secure headers

7. **Code Quality**
   - Linting compliance
   - Formatting standards
   - Naming conventions
   - Code complexity limits
   - No code duplication

Validate against documentation:
- API usage: {documentation.api_reference}
- Best practices: {documentation.best_practices}
- Deprecated methods: {documentation.deprecated}
- Security patterns: {documentation.security_patterns}

IMPORTANT: All code must pass documentation validation with score >= 90/100
"""

# QA Engineer Agent Template
QA_TEMPLATE = """
As a Senior QA Engineer agent, create and execute comprehensive test plans.

Module to Test: {module}
Requirements: {requirements}
Code Base: {code_base}
Documentation: {documentation}

Deliver:

1. **Test Strategy**
   - Testing approach
   - Test levels (unit, integration, system, acceptance)
   - Test types (functional, performance, security, usability)
   - Entry/Exit criteria
   - Risk-based testing focus

2. **Test Plan**
   - Test scenarios
   - Test cases with steps
   - Test data requirements
   - Environment requirements
   - Testing schedule

3. **Test Implementation**
   - Automated test scripts
   - Test fixtures
   - Mock objects
   - Test utilities
   - CI/CD integration

4. **Test Coverage**
   - Code coverage analysis
   - Requirements coverage
   - Risk coverage
   - Browser/device coverage
   - API endpoint coverage

5. **Performance Testing**
   - Load test scenarios
   - Stress test plans
   - Performance benchmarks
   - Bottleneck identification
   - Optimization recommendations

6. **Security Testing**
   - Vulnerability scanning
   - Penetration test cases
   - OWASP compliance
   - Security best practices
   - Threat modeling

7. **Test Results**
   - Test execution report
   - Defect report
   - Coverage metrics
   - Performance metrics
   - Recommendations

Reference testing best practices: {documentation.testing_patterns}
Use documented test utilities: {documentation.test_frameworks}
"""

# Code Reviewer Agent Template
CODE_REVIEWER_TEMPLATE = """
As a Senior Code Reviewer agent, perform comprehensive code review.

Code to Review: {code}
Requirements: {requirements}
Standards: {coding_standards}
Documentation: {documentation}

Provide detailed review covering:

1. **Code Quality**
   - Clean Code principles
   - SOLID principles
   - DRY principle
   - KISS principle
   - YAGNI principle

2. **Functionality**
   - Requirements compliance
   - Logic correctness
   - Edge case handling
   - Input validation
   - Output correctness

3. **Performance**
   - Algorithm complexity
   - Database queries
   - Memory usage
   - Network calls
   - Caching usage

4. **Security**
   - Vulnerability assessment
   - Input sanitization
   - Authentication/Authorization
   - Data encryption
   - Security headers

5. **Maintainability**
   - Code readability
   - Documentation quality
   - Test coverage
   - Modularity
   - Coupling/Cohesion

6. **Best Practices**
   - Language-specific patterns
   - Framework conventions
   - Industry standards
   - Team guidelines
   - Documentation standards

7. **Specific Issues**
   For each issue found:
   - Severity (Critical/Major/Minor)
   - Location (file:line)
   - Description
   - Recommendation
   - Code example

8. **Improvement Suggestions**
   - Refactoring opportunities
   - Performance optimizations
   - Security enhancements
   - Test improvements
   - Documentation additions

Validate against documentation:
- Deprecated APIs: {documentation.deprecated_apis}
- Security vulnerabilities: {documentation.security_advisories}
- Performance anti-patterns: {documentation.performance_issues}
- Accessibility violations: {documentation.accessibility_rules}

Overall Score: X/10
Recommendation: [Approve/Request Changes/Reject]
"""

# DevOps Engineer Agent Template
DEVOPS_TEMPLATE = """
As a Senior DevOps Engineer agent, create complete infrastructure and deployment setup.

Architecture: {architecture}
Requirements: {requirements}
Documentation: {documentation}

Provide:

1. **Container Configuration**
   - Dockerfile optimization
   - Docker-compose setup
   - Multi-stage builds
   - Security scanning
   - Image optimization

2. **Kubernetes Manifests**
   - Deployment configurations
   - Service definitions
   - ConfigMaps/Secrets
   - Ingress rules
   - Auto-scaling policies

3. **CI/CD Pipeline**
   - Build pipeline
   - Test automation
   - Security scanning
   - Deployment stages
   - Rollback strategy

4. **Infrastructure as Code**
   - Terraform/CloudFormation
   - Resource definitions
   - Network configuration
   - Security groups
   - Monitoring setup

5. **Monitoring & Logging**
   - Metrics collection
   - Log aggregation
   - Alert rules
   - Dashboards
   - Tracing setup

6. **Security Configuration**
   - Secret management
   - Network policies
   - RBAC setup
   - Security scanning
   - Compliance checks

7. **Deployment Strategy**
   - Blue-green deployment
   - Canary releases
   - Feature flags
   - Rollback procedures
   - Disaster recovery

Reference cloud best practices: {documentation.cloud_patterns}
Follow security guidelines: {documentation.security_standards}
"""

# Export all templates
AGENT_TEMPLATES = {
    'product_manager': PM_TEMPLATE,
    'business_analyst': BA_TEMPLATE,
    'uiux_designer': UIUX_TEMPLATE,
    'architect': ARCHITECT_TEMPLATE,
    'developer': DEVELOPER_TEMPLATE,
    'qa_engineer': QA_TEMPLATE,
    'code_reviewer': CODE_REVIEWER_TEMPLATE,
    'devops_engineer': DEVOPS_TEMPLATE
}


def get_agent_template(agent_type: str, **kwargs) -> str:
    """
    Get formatted template for specific agent type
    
    Args:
        agent_type: Type of agent
        **kwargs: Template variables
        
    Returns:
        Formatted template string
    """
    template = AGENT_TEMPLATES.get(agent_type)
    if not template:
        raise ValueError(f"Unknown agent type: {agent_type}")
        
    # Add default documentation if not provided
    if 'documentation' not in kwargs:
        kwargs['documentation'] = "No documentation available"
        
    return template.format(**kwargs)


def get_agent_chain(project_type: str) -> list:
    """
    Get recommended agent chain for project type
    
    Args:
        project_type: Type of project (web, mobile, api, etc.)
        
    Returns:
        Ordered list of agent types
    """
    chains = {
        'web': [
            'product_manager',
            'business_analyst',
            'uiux_designer',
            'architect',
            'developer',
            'qa_engineer',
            'code_reviewer',
            'devops_engineer'
        ],
        'api': [
            'product_manager',
            'business_analyst',
            'architect',
            'developer',
            'qa_engineer',
            'code_reviewer',
            'devops_engineer'
        ],
        'mobile': [
            'product_manager',
            'business_analyst',
            'uiux_designer',
            'architect',
            'developer',
            'qa_engineer',
            'code_reviewer'
        ],
        'microservice': [
            'architect',
            'developer',
            'qa_engineer',
            'code_reviewer',
            'devops_engineer'
        ]
    }
    
    return chains.get(project_type, chains['web'])
