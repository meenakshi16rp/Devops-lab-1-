# ENSP461 Lab 1 - DevOps Foundations & Continuous Integration

Sample Flask application with a complete Jenkins CI/CD pipeline.

**Author:** Meenakshi | **Course:** ENSP461 - DevOps & Automation | **Lab:** 1

## Repository structure
- `app/` - Sample Flask application and unit tests
- `deploy/` - Automated deployment script
- `docs/` - Command logs, screenshots and observations
- `Jenkinsfile` - Declarative pipeline (Build / Test / Deploy)

## Pipeline
1. **Checkout** - pulls source from GitHub
2. **Build** - creates virtualenv, installs dependencies
3. **Test** - runs pytest unit tests
4. **Deploy** - runs deploy script, verifies health endpoint
