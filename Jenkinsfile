pipeline {
    agent any

    environment {
        APP_NAME = "EcommerceService"
        VERSION = "1.2.0"
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
                echo "Building application..."

                sh 'mvn clean package'
            }
        }

        stage('Test') {
            steps {
                echo "Running test cases..."

                sh 'mvn test'
            }
        }

        stage('SonarQube Scan') {
            steps {
                echo "Executing code quality scan..."

                sh 'mvn sonar:sonar'
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."

                sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker build -t ecommerce-service:$VERSION .
                else
                    echo "docker is not installed on this runner, skipping this step."
                fi
                '''
            }
        }

        stage('Push Image') {
            steps {
                echo "Pushing Docker image..."

                sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker push ecommerce-service:$VERSION
                else
                    echo "docker is not installed on this runner, skipping this step."
                fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying application to Kubernetes..."

                sh '''
                if command -v kubectl >/dev/null 2>&1; then
                    kubectl apply -f k8s/deployment.yaml
                else
                    echo "kubectl is not installed on this runner, skipping this step."
                fi
                '''
            }
        }
    }

    post {

        success {
            echo "Deployment completed successfully"
        }

        always {
            echo "Cleaning workspace..."

            cleanWs()
        }
    }
}
