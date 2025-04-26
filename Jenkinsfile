pipeline {
    agent any

    environment {
        // Credentials IDs in Jenkins
        GIT_CREDENTIALS = 'github-ssh'
        // Other environment variables...
        ACR_NAME = 'ranjeet'
        IMAGE_NAME = "${ACR_NAME}.azurecr.io/webapp:${BUILD_ID}"
        AZURE_CREDENTIALS = 'your-azure-service-principal-credentials' // Use the ID of your Azure Service Principal credential
        DEPLOYMENT_NAME = 'webapp-deployment'
        NAMESPACE = 'default'
        DOCKERFILE_PATH = 'webapp'
        K8S_MANIFEST_PATH = 'k8s'
        APP_NAME = 'webapp'
        REGISTRY_CREDENTIALS = 'acr-credentials'
        RESOURCE_GROUP = 'your-resource-group-name'  // Add your resource group
        AKS_CLUSTER_NAME = 'your-aks-cluster-name'      // Add your AKS cluster name
    }

    stages {
        stage('Checkout') {
            steps {
                // Use credentialsId for Git
                git credentialsId: env.GIT_CREDENTIALS, url: 'https://github.com/ranjeetchavan7/simple-webapp.git', branch: 'main'
            }
        }

        stage('Build and Test') {
            steps {
                script {
                    echo "Setting up virtual environment and installing dependencies for ${env.APP_NAME}"
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate'
                    sh "python3 -m pip install -r requirements.txt"
                    echo "Running tests for ${env.APP_NAME}"
                    if (fileExists("${env.DOCKERFILE_PATH}/tests")) {
                        sh "python3 -m unittest discover ${env.DOCKERFILE_PATH}/tests"
                    } else {
                        echo "No tests directory found in ${env.DOCKERFILE_PATH}. Skipping tests."
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS, passwordVariable: 'REGISTRY_PASSWORD', usernameVariable: 'REGISTRY_USERNAME')]) {
                    echo "Building Docker image: ${env.IMAGE_NAME}"
                    sh "docker build -f Dockerfile -t ${env.APP_NAME} ."
                    sh "docker tag ${env.APP_NAME} ${env.IMAGE_NAME}"
                    echo "Logging into Azure Container Registry: ${env.ACR_NAME}.azurecr.io"
                    sh "docker login -u ${env.REGISTRY_USERNAME} -p ${env.REGISTRY_PASSWORD} ${env.ACR_NAME}.azurecr.io"
                    echo "Pushing Docker image: ${env.IMAGE_NAME}"
                    sh "docker push ${env.IMAGE_NAME}"
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                // Use the Azure Credentials plugin
                azureCredentials(credentialsId: env.AZURE_CREDENTIALS) {
                    script {
                        echo "Deploying to AKS..."
                        // IMPORTANT:  Use 'az' commands within the script block.
                        // Get AKS credentials
                        sh "az aks get-credentials --resource-group \"${env.RESOURCE_GROUP}\" --name \"${env.AKS_CLUSTER_NAME}\" --file \"${WORKSPACE}/.kube/config\""

                        // Deploy Kubernetes manifests, using the kubeconfig
                        sh "kubectl apply -f ${env.K8S_MANIFEST_PATH}/deployment.yaml -n ${env.NAMESPACE} --kubeconfig=\"${WORKSPACE}/.kube/config\""
                        sh "kubectl apply -f ${env.K8S_MANIFEST_PATH}/service.yaml -n ${env.NAMESPACE} --kubeconfig=\"${WORKSPACE}/.kube/config\""
                        echo "Successfully deployed ${env.APP_NAME} to AKS namespace ${env.NAMESPACE}"
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    def serviceName = "${env.APP_NAME}-service"
                    def namespace = env.NAMESPACE
                    def maxRetries = 5
                    def retryInterval = 30
                    withCredentials([file(credentialsId: env.AZURE_CREDENTIALS, variable: 'KUBECONFIG_FILE')]) {
                        for (int i = 0; i < maxRetries; i++) {
                            try {
                                def serviceInfo = sh(script: "kubectl --kubeconfig=\"${KUBECONFIG_FILE}\" get service ${serviceName} -n ${namespace} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'", returnStdout: true).trim()
                                if (serviceInfo) {
                                    echo "Service ${serviceName} is available at: ${serviceInfo}"
                                    sh "curl --fail --show-error http://${serviceInfo}"
                                    break
                                } else {
                                    echo "LoadBalancer IP for ${serviceName} not yet available. Retrying in ${retryInterval} seconds (${i + 1}/${maxRetries})..."
                                    sleep time: retryInterval, unit: 'SECONDS'
                                }
                            } catch (Exception e) {
                                echo "Error checking service status: ${e.getMessage()}"
                                if (i < maxRetries - 1) {
                                    sleep time: retryInterval, unit: 'SECONDS'
                                } else {
                                    error "Failed to verify deployment of ${serviceName} after ${maxRetries} retries."
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed for ${env.APP_NAME}."
        }
        failure {
            echo "Pipeline failed for ${env.APP_NAME} :("
        }
        success {
            echo "Pipeline succeeded for ${env.APP_NAME}!"
        }
    }
}

