pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip --break-system-packages
                    python3 -m pip install -r ./backend/requirements.txt --break-system-packages
                '''
            }
        }
        stage('Lint') {
            steps {
                sh '''
                    python3 -m pip install flake8 --break-system-packages
                    cd backend
                    python3 -m flake8 . --exit-zero
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    cd backend
                    python3 -m pytest || [ $? -eq 5 ]
                '''
            }
        }
        stage('Archive') {
            steps {
                echo 'No build artifacts to archive for Python/JS project.'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploy stage placeholder.'
            }
        }
    }
    post {
        always {
            echo 'Cleaning workspace...'
            cleanWs()
        }
    }
}