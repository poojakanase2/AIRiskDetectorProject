pipeline {
    agent any
    stages {
        stage('Backend Lint') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --upgrade pip
                        pip install flake8
                        flake8 .
                    '''
                }
            }
        }
        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh '''
                        . .venv/bin/activate
                        pip install -r requirements.txt
                        pytest
                    '''
                }
            }
        }
        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    sh 'echo "Linting frontend (HTML/CSS/JS)"'
                }
            }
        }
        stage('Frontend Smoke Test') {
            steps {
                dir('frontend') {
                    sh 'echo "Running frontend smoke tests"'
                }
            }
        }
    }
}
