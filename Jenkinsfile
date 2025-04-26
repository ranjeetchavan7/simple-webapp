pipeline {
    agent {
        // Specify a specific agent or label, or use 'any'
        any
    }
    environment {
        // Define environment variables for your project.  Good practice to define them here.
        AZURE_CREDENTIALS = 'my-aks-service-principal' // Use the ID from your Jenkins credentials
        RESOURCE_GROUP = 'my-acr-rg'  // Replace with your actual resource group
        AKS_CLUSTER_NAME = 'MyAKSCluster'    // Replace with your actual AKS cluster name
        REGISTRY_NAME    = 'ranjeet'          // Replace with your ACR name
        REGISTRY_PASSWORD = credentials('acr-credentials') // Use the ID of your ACR credentials in Jenkins
        DOCKER_IMAGE_TAG = "latest" // Or a build number, e.g., "${BUILD_NUMBER}"
        K8S_MANIFEST_PATH = 'k8s'       // Relative path to your Kubernetes manifests in the repo
        NAMESPACE = 'default'         // Kubernetes namespace to deploy to
        APP_NAME = 'webapp'
    }
    stages {
        stage('Checkout') {
            steps {
                git(
                    credentialsId: 'github-ssh', // Use the ID of your GitHub credential
                    url: 'https://github.com/ranjeetchavan7/simple-webapp.git',
                    branch: 'main' // Or your desired branch
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
                    // Add your test commands here.  For example:
                    // sh 'python3 -m pytest'
                    if (fileExists('tests')) {
                        sh 'python -m unittest discover -s tests'
                    }
                    else {
                         echo "No tests directory found in webapp. Skipping tests."
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                withCredentials(credentials: [usernamePassword(credentialsId: 'acr-credentials', usernameVariable: 'REGISTRY_USERNAME', passwordVariable: 'REGISTRY_PASSWORD')]) {
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
                // Use the Azure Credentials plugin to handle authentication
                azureCredentials(credentialsId: AZURE_CREDENTIALS) {  // Use the variable
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
                //  Add steps to verify the deployment, e.g., check pod status
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
            //  Add any cleanup steps here
        }
        failure {
            echo "Pipeline failed for ${APP_NAME} :("
        }
    }
}
