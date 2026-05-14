pipeline {
    agent any

    environment {
        APP_NAME = "AnalyticsService"
        IMAGE_TAG = "v2.0"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Fetching source code..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Compile') {
            steps {
                echo "Compiling project..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean compile
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                        exit 0
                    fi
                '''
            }
        }

        stage('Unit Test') {
            steps {
                echo "Running unit tests..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn test
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                        exit 0
                    fi
                '''
            }
        }

        stage('Package') {
            steps {
                echo "Packaging application..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn package
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                        exit 0
                    fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Creating Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t analytics-service:$IMAGE_TAG .
                    else
                        echo "docker is not installed on this runner, skipping this step."
                        exit 0
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application..."
                sh '''
                    if command -v kubectl >/dev/null 2>&1; then
                        kubectl apply -f deployment.yaml
                    else
                        echo "kubectl is not installed on this runner, skipping this step."
                        exit 0
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Deployment failed"
        }
    }
}
