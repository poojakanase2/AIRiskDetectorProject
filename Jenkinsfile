pipeline {
    agent any

    environment {
        APP_NAME = "CustomerService"
        DOCKER_TAG = "latest"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning GitHub repository..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Building Java application..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean install
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                    fi
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Executing unit tests..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn test
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                    fi
                '''
            }
        }

        stage('Docker Push') {
            steps {
                echo "Pushing Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker push customer-service:$DOCKER_TAG
                    else
                        echo "docker is not installed on this runner, skipping this step."
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
            echo "Build failed"
        }
    }
}
