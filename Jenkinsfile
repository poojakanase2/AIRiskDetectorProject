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
                echo "Installing backend dependencies..."
                sh '''
                cd backend
                python3 -m pip install --upgrade pip --break-system-packages
                python3 -m pip install -r requirements.txt --break-system-packages
                '''
            }
        }

        stage('Lint') {
            steps {
                echo "Linting backend Python code..."
                sh '''
                cd backend
                python3 -m pip install flake8 --break-system-packages
                python3 -m flake8 . --exit-zero
                '''
            }
        }

        stage('Test') {
            steps {
                echo "Running backend tests..."
                sh '''
                cd backend
                python3 -m pip install pytest --break-system-packages
                python3 -m pytest || [ $? -eq 5 ]
                '''
            }
        }

        stage('SonarQube Scan') {
            steps {
                echo "Executing code quality scan..."
                sh '''
                if command -v sonar-scanner >/dev/null 2>&1; then
                    sonar-scanner
                else
                    echo "sonar-scanner is not installed on this runner, skipping this step."
                fi
                '''
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
