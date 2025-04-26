pipeline {
    agent any

    environment {
        // Define environment variables for your project.
        AZURE_CREDENTIALS = 'my-aks-service-principal'
        RESOURCE_GROUP = 'my-acr-rg'
        AKS_CLUSTER_NAME = 'MyAKSCluster'
        REGISTRY_NAME = 'ranjeet'
        REGISTRY_PASSWORD = credentials('acr-credentials')  // Use credentials() here.
        DOCKER_IMAGE_TAG = "latest"
        K8S_MANIFEST_PATH = 'k8s'
        NAMESPACE = 'default'
        APP_NAME = 'webapp'
    }
    stages {
        stage('Checkout') {
            steps {
                git(
                    credentialsId: 'github-ssh',
                    url: 'https://github.com/ranjeetchavan7/simple-webapp.git',
                    branch: 'main'
                )
            }
        }
        stage('Build and Test') {
            steps {
                script {
                    echo "Setting up virtual environment and installing dependencies for webapp"
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate'
                    sh 'python3 -m pip install -r requirements.txt'
                    echo "Running tests for webapp"
                    if (fileExists('tests')) {
                        sh 'python -m unittest discover -s tests'
                    } else {
                        echo "No tests directory found in webapp. Skipping tests."
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                withCredentials(bindings: [usernamePassword(credentialsId: 'acr-credentials', usernameVariable: 'REGISTRY_USERNAME', passwordVariable: 'REGISTRY_PASSWORD')]) {
                    script {
                        echo "Building Docker image: ${REGISTRY_NAME}.azurecr.io/${APP_NAME}:${DOCKER_IMAGE_TAG}"
                        sh "docker build -f Dockerfile -t ${APP_NAME} ."
                        sh "docker tag ${APP_NAME} ${REGISTRY_NAME}.azurecr.io/${APP_NAME}:${DOCKER_IMAGE_TAG}"
                        echo "Logging into Azure Container Registry: ${REGISTRY_NAME}.azurecr.io"
                        sh "docker login -u '${REGISTRY_USERNAME}' -p '${REGISTRY_PASSWORD}' ${REGISTRY_NAME}.azurecr.io"
                        echo "Pushing Docker image: ${REGISTRY_NAME}.azurecr.io/${APP_NAME}:${DOCKER_IMAGE_TAG}"
                        sh "docker push ${REGISTRY_NAME}.azurecr.io/${APP_NAME}:${DOCKER_IMAGE_TAG}"
                    }
                }
            }
        }
        stage('Deploy to AKS') {
            steps {
                //  Use the Azure Credentials plugin to handle authentication
                azureCredentials(credentialsId: AZURE_CREDENTIALS) {
                    script {
                        echo "Deploying to AKS..."
                        // Get AKS credentials using az cli
                        sh "az aks get-credentials --resource-group '${RESOURCE_GROUP}' --name '${AKS_CLUSTER_NAME}' --file '\${WORKSPACE}/.kube/config'"

                        // Deploy Kubernetes manifests
                        sh "kubectl apply -f ${K8S_MANIFEST_PATH}/deployment.yaml -n ${NAMESPACE} --kubeconfig=\${WORKSPACE}/.kube/config"
                        sh "kubectl apply -f ${K8S_MANIFEST_PATH}/service.yaml -n ${NAMESPACE} --kubeconfig=\${WORKSPACE}/.kube/config"
                        echo "Successfully deployed to AKS"
                    }
                }
            }
        }
        stage('Verify Deployment') {
            steps {
                script {
                    echo "Verifying Deployment..."
                    sh "kubectl get deployment ${APP_NAME} -n ${NAMESPACE} --kubeconfig=\${WORKSPACE}/.kube/config -o wide"
                    sh "kubectl get service ${APP_NAME} -n ${NAMESPACE} --kubeconfig=\${WORKSPACE}/.kube/config -o wide"
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline completed for ${APP_NAME}."
        }
        failure {
            echo "Pipeline failed for ${APP_NAME} :("
        }
    }
}

