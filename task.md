# Choice Based Conjoint Design Generator MCP Server
## Task Breakdown Document

### Phase 1: Project Setup and Foundation (Week 1)

#### Task 1.1: Development Environment Setup
- **1.1.1** Initialize Python project structure — Completed (2025-09-23)
- **1.1.2** Setup virtual environment and dependencies — In Progress
- **1.1.3** Configure development tools (linting, testing, etc.) — Completed (2025-09-23)
- **1.1.4** Create basic MCP server skeleton — Completed (2025-09-23)
- **1.1.5** Setup version control and branching strategy — Pending

#### Task 1.2: MCP Server Foundation
- **1.2.1** Implement basic MCP protocol handlers — Completed (ping/health)
- **1.2.2** Create request/response data models — Completed (initial set)
- **1.2.3** Setup error handling framework — Pending
- **1.2.4** Implement logging system — Completed (basic)
- **1.2.5** Create configuration management — Completed (pydantic Settings)

### Phase 2: Core Algorithm Implementation (Weeks 2-3)

#### Task 2.1: Design Parameter Optimization
- **2.1.1** Implement statistical power calculations — Completed (2025-09-23)
- **2.1.2** Create respondent size optimization algorithm — Completed (2025-09-23)
- **2.1.3** Develop screen count optimization — Completed (2025-09-23)
- **2.1.4** Build options-per-screen optimization — Completed (2025-09-23)
- **2.1.5** Integrate efficiency metrics calculation — Completed (2025-09-23)

#### Task 2.2: Basic Design Generation
 - **2.2.1** Implement random design generator — Completed (2025-09-23)
 - **2.2.2** Create balanced overlap algorithm — Completed (2025-09-23)
 - **2.2.3** Build orthogonal array generator — Completed (2025-09-23)
 - **2.2.4** Implement design validation functions — Completed (duplicate level checks)
 - **2.2.5** Create design quality metrics — Completed (level balance score)

#### Task 2.3: D-Optimal Design Implementation
- **2.3.1** Research and implement D-optimal algorithm — Completed (2025-09-23)
- **2.3.2** Create information matrix calculations — Completed (2025-09-23)
- **2.3.3** Implement design search and optimization — Completed (2025-09-23)
- **2.3.4** Add convergence criteria and stopping rules — Completed (2025-09-23)
- **2.3.5** Optimize algorithm performance — Completed (2025-09-23)

Notes: Balanced overlap and orthogonal array have placeholder implementations that currently delegate to the random generator; to be replaced with proper algorithms.

### Phase 3: Advanced Features (Week 4)

#### Task 3.1: Constraint Management System
- **3.1.1** Design constraint data structures — Completed (2025-09-23)
- **3.1.2** Implement prohibited combinations handling — Completed (2025-09-23)
- **3.1.3** Create required combinations enforcement — Completed (2025-09-23)
- **3.1.4** Build level balance constraints — Completed (2025-09-23)
- **3.1.5** Develop custom rule engine — Completed (2025-09-23)

#### Task 3.2: Output Generation System
- **3.2.1** Implement CSV export functionality — Completed (2025-09-23)
- **3.2.2** Create design validation reports — Completed (2025-09-23)
- **3.2.3** Build design documentation generator — Completed (2025-09-23)
- **3.2.4** Add multiple output format support — Completed (2025-09-23)
- **3.2.5** Implement data quality checks — Completed (2025-09-23)

### Phase 4: Integration and Testing (Week 5)

#### Task 4.1: MCP Integration
- **4.1.1** Connect algorithms to MCP endpoints — Completed (2025-09-23)
- **4.1.2** Implement request parsing and validation — Completed (2025-09-23)
- **4.1.3** Create response formatting — Completed (2025-09-23)
- **4.1.4** Add comprehensive error handling — Completed (2025-09-23)
- **4.1.5** Implement request logging and monitoring — Completed (2025-09-23)

#### Task 4.2: Testing Framework
- **4.2.1** Setup unit testing framework — Completed (pytest configured)
- **4.2.2** Create integration tests for MCP methods — Completed (2025-09-23)
- **4.2.3** Implement algorithm accuracy tests — Completed (2025-09-23)
- **4.2.4** Build performance benchmarking tests — Completed (2025-09-23)
- **4.2.5** Create end-to-end testing scenarios — Completed (2025-09-23)

### Phase 5: Local Deployment and Validation (Week 6)

#### Task 5.1: Local Testing Environment
- **5.1.1** Create local testing scripts — Completed (2025-09-23)
- **5.1.2** Build sample design scenarios — Completed (2025-09-23)
- **5.1.3** Implement interactive testing interface — Completed (2025-09-23)
- **5.1.4** Create performance monitoring — Completed (2025-09-23)
- **5.1.5** Document local setup procedures — Completed (2025-09-23)

#### Task 5.2: Documentation and Examples
- **5.2.1** Write API documentation — Completed (2025-09-23)
- **5.2.2** Create usage examples — Completed (2025-09-23)
- **5.2.3** Build troubleshooting guides — Completed (2025-09-23)
- **5.2.4** Document algorithm implementations — Completed (2025-09-23)
- **5.2.5** Create deployment guides — Completed (2025-09-23)

### Phase 6: Heroku Deployment Preparation (Week 7)

#### Task 6.1: Cloud Readiness
- **6.1.1** Configure environment variables
- **6.1.2** Optimize for Heroku constraints
- **6.1.3** Implement health check endpoints
- **6.1.4** Setup logging for cloud environment
- **6.1.5** Create deployment configurations

#### Task 6.2: Heroku Deployment
- **6.2.1** Create Heroku application
- **6.2.2** Configure buildpacks and dependencies
- **6.2.3** Deploy initial version
- **6.2.4** Setup monitoring and logging
- **6.2.5** Validate cloud deployment

### Phase 7: Final Testing and Documentation (Week 8)

#### Task 7.1: End-to-End Testing
- **7.1.1** Test all MCP methods in cloud environment
- **7.1.2** Validate design quality across scenarios
- **7.1.3** Performance testing under load
- **7.1.4** Error handling validation
- **7.1.5** User acceptance testing

#### Task 7.2: Project Completion
- **7.2.1** Final documentation review
- **7.2.2** Code cleanup and optimization
- **7.2.3** Create deployment runbook
- **7.2.4** Package final deliverables
- **7.2.5** Project handover preparation

### Ongoing Tasks (Throughout Project)

#### Continuous Integration
- **CI.1** Daily code reviews and quality checks
- **CI.2** Weekly integration testing
- **CI.3** Performance monitoring and optimization
- **CI.4** Documentation updates
- **CI.5** Dependency management and security updates

### Risk Mitigation Tasks
### Discovered During Work

- Add pre-commit hooks for formatting/linting
- Validate JSON-RPC request schema and error codes
- Replace minimal stdio loop with official `mcp-server-python` server once integrated
 - Add CI job to run tests and lint on push


#### High-Risk Areas
- **RM.1** Algorithm complexity validation
- **RM.2** Memory optimization for large designs
- **RM.3** MCP protocol compliance verification
- **RM.4** Heroku deployment constraints handling
- **RM.5** Performance optimization under cloud limits

#### Discovered During Work
- **2025-01-23**: Implemented Johnson-Orme rule for CBC sample size calculation
  - Replaced all previous methods with academically validated Johnson-Orme rule
  - Formula: n ≥ 500c / (t × a) for main effects
  - Support for interaction analysis with largest product of attribute levels
  - Includes 15% quality buffer for dropouts and quality loss
  - Laptop design now suggests 49 respondents (main effects) vs previous 68
  - Matches academic literature examples and industry best practices
  - Added comprehensive recommendations function with multiple scenarios