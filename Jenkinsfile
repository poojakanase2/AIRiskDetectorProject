pipeline {
    agent any
    stages {
        stage('Backend Lint') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        .venv/bin/pip install --upgrade pip
                        .venv/bin/pip install flake8
                        .venv/bin/flake8 .
                    '''
                }
            }
        }
        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh '''
                        . .venv/bin/activate
                        .venv/bin/pip install -r requirements.txt
                        .venv/bin/python -m pytest
                    '''
                }
            }
        }
        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    sh '''
                        echo "Linting frontend (HTML/CSS/JS)"
                        # Add custom lint commands if needed
                    '''
                }
            }
        }
        stage('Frontend Smoke Test') {
            steps {
                dir('frontend') {
                    sh '''
                        echo "Running frontend smoke tests"
                        # Add custom smoke test commands if needed
                    '''
                }
            }
        }
    }
}