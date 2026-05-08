pipeline {
    agent any
    stages {
        stage('Backend Lint') {
            steps {
                dir('backend') {
                    // Remove venv creation, install dependencies directly
                    sh 'python3 -m pip install --upgrade pip --break-system-packages'
                    sh 'python3 -m pip install flake8 --break-system-packages'
                    sh 'flake8 .'
                }
            }
        }
        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install --upgrade pip --break-system-packages'
                    sh 'python3 -m pip install pytest --break-system-packages'
                    sh 'pytest'
                }
            }
        }
        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    // No npm or linter needed, placeholder for HTML/CSS/JS
                    sh 'echo "Frontend linting skipped (no linter configured)"'
                }
            }
        }
        stage('Frontend Smoke Test') {
            steps {
                dir('frontend') {
                    sh 'echo "Frontend smoke test placeholder"'
                }
            }
        }
    }
}
