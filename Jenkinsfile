pipeline {
    agent any

    environment {
        APP_NAME = "UserService"
        ENV = "production"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Compiling application..."
                sh 'mvn clean package'
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh 'mvn test'
            }
        }

        stage('Archive') {
            steps {
                echo "Archiving artifacts..."
                archiveArtifacts artifacts: 'target/*.jar'
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."
                sh "kubectl apply -f deployment.yaml"
            }
        }
    }

    post {
        success {
            echo "Deployment completed"
        }
        always {
            echo "Cleaning workspace..."
            cleanWs()
        }
    }
}
