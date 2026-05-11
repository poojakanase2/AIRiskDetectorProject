pipeline {
    agent any
    stages {
        stage('Backend Lint') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install --upgrade pip --break-system-packages'
                    sh 'python3 -m pip install flake8 --break-system-packages'
                    sh 'python3 -m flake8 . --exit-zero'
                }
            }
        }
        stage('Backend Test') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install pytest --break-system-packages'
                    sh 'python3 -m pytest'
                }
            }
        }
        stage('Frontend Lint') {
            steps {
                dir('frontend') {
                    echo 'No linting required for vanilla HTML/CSS/JS.'
                }
            }
        }
        stage('Frontend Smoke Test') {
            steps {
                dir('frontend') {
                    echo 'No build required for vanilla HTML/CSS/JS.'
                }
            }
        }
    }
}
