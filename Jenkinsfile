pipeline {
    agent any

    environment {
        AZURE_CREDENTIALS = credentials('my-aks-service-principal') // your Azure credential ID
        AZURE_SUBSCRIPTION_ID = 'your-azure-subscription-id'         // your Azure subscription ID
        RESOURCE_GROUP = 'your-resource-group'
        AKS_CLUSTER = 'your-aks-cluster-name'
        ACR_NAME = 'your-acr-name'
        DOCKER_IMAGE_NAME = 'simple-webapp'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/ranjeetchavan7/simple-webapp.git'
            }
        }

        stage('Azure CLI Login') {
            steps {
                script {
                    echo 'Logging into Azure using Service Principal credentials...'
                    sh """
                        az login --service-principal -u '${AZURE_CREDENTIALS.clientId}' -p '${AZURE_CREDENTIALS.clientSecret}' --tenant '${AZURE_CREDENTIALS.tenantId}'
                        az account set --subscription '${AZURE_SUBSCRIPTION_ID}'
                    """
                }
            }
        }

        stage('Build and Test') {
            steps {
                echo 'Building and testing application...'
                sh 'echo "Simulate Build and Test Stage"'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker Image...'
                    sh """
                        docker build -t ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE_NAME}:latest .
                    """
                }
            }
        }

        stage('Push Docker Image to ACR') {
            steps {
                script {
                    echo 'Logging into Azure Container Registry and pushing image...'
                    sh """
                        az acr login --name ${ACR_NAME}
                        docker push ${ACR_NAME}.azurecr.io/${DOCKER_IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    echo 'Deploying to AKS...'
                    sh """
                        az aks get-credentials --resource-group ${RESOURCE_GROUP} --name ${AKS_CLUSTER} --overwrite-existing
                        kubectl apply -f k8s-deployment.yaml
                        kubectl apply -f k8s-service.yaml
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment...'
                sh 'kubectl get pods'
                sh 'kubectl get svc'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! 🎉'
        }
        failure {
            echo 'Pipeline failed 😢'
        }
    }
}
