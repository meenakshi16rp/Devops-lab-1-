// ENSP461 Lab 1 - Declarative CI/CD pipeline
// Stages: Build -> Test -> Deploy, triggered from GitHub
pipeline {
    agent any

    environment {
        VENV = "$WORKSPACE/.venv"
        DEPLOY_DIR = "$HOME/enp461-deploy"
    }

    stages {
        stage("Checkout") {
            steps {
                echo "Pulling source code from GitHub repository..."
                checkout scm
            }
        }

        stage("Build") {
            steps {
                echo "Building application: creating virtual environment and installing dependencies..."
                sh """
                    python3 -m venv $VENV
                    $VENV/bin/pip install --quiet -r app/requirements.txt
                """
            }
        }

        stage("Test") {
            steps {
                echo "Running unit tests with pytest..."
                sh "$VENV/bin/python -m pytest app/tests -v"
            }
        }

        stage("Deploy") {
            steps {
                echo "Deploying application to local deployment directory..."
                sh "./deploy/deploy.sh"
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS: application built, tested and deployed."
        }
        failure {
            echo "Pipeline FAILED - check the stage logs."
        }
        always {
            echo "Cleaning workspace temporary files..."
            cleanWs()
        }
    }
}
