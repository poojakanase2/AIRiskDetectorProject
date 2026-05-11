pipeline {
    agent any

    environment {
        APP_NAME = "PaymentService"
        DOCKER_IMAGE = "payment-app"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."

                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Building application..."

                sh 'mvn clean package'
            }
        }

        stage('Test') {
            steps {
                echo "Running unit tests..."

                sh 'mvn test'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Creating Docker image..."

                sh 'docker build -t payment-app:v1 .'
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."

                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }

    post {

        success {
            echo "Build completed successfully"
        }

        always {
            echo "Cleaning workspace..."

            cleanWs()
        }
    }
}
