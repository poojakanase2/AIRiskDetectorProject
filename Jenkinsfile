pipeline {
    agent any

    environment {
        APP_NAME = "InventoryManager"
        IMAGE_NAME = "inventory-manager:v1"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out code from repository..."
                git url: 'https://github.com/poojakanase2/AIRiskDetectorProject.git', branch: 'main'
            }
        }

        stage('Build') {
            steps {
                echo "Building project using Maven..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn clean package
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                    fi
                '''
            }
        }

        stage('Code Quality') {
            steps {
                echo "Running code quality scan..."
                sh '''
                    if command -v mvn >/dev/null 2>&1; then
                        mvn sonar:sonar
                    else
                        echo "mvn is not installed on this runner, skipping this step."
                    fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image..."
                sh '''
                    if command -v docker >/dev/null 2>&1; then
                        docker build -t $IMAGE_NAME .
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
            echo "Pipeline executed successfully"
        }
        always {
            echo "Removing temporary files..."
            cleanWs()
        }
    }
}
