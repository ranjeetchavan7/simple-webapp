pipeline {
    agent any

    environment {
        // Credentials IDs in Jenkins
        GIT_CREDENTIALS = 'github-ssh'
        // Other environment variables...
        ACR_NAME = 'ranjeet'
        IMAGE_NAME = "${ACR_NAME}.azurecr.io/webapp:${BUILD_ID}"
        KUBE_CONFIG_CREDENTIALS = 'my-aks-service-principal'
        DEPLOYMENT_NAME = 'webapp-deployment'
        NAMESPACE = 'default'
        DOCKERFILE_PATH = 'webapp'  // Corrected: Consistent variable name
        K8S_MANIFEST_PATH = 'k8s'
        APP_NAME = 'webapp'
        REGISTRY_CREDENTIALS = 'acr-credentials'
        RESOURCE_GROUP = 'my-rg'
        AKS_CLUSTER_NAME = 'my-aks'
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
                    //sh "docker build -f Dockerfile -t ${env.APP_NAME} ." // Incorrect, Dockerfile is in a subfolder
                    sh "docker build -f ${env.DOCKERFILE_PATH}/Dockerfile -t ${env.IMAGE_NAME} ."  // Corrected: added DOCKERFILE_PATH to path, and changed the tag to IMAGE_NAME
                    sh "docker tag ${env.IMAGE_NAME} ${env.IMAGE_NAME}" //redundant line, removed.
                    echo "Logging into Azure Container Registry: ${env.ACR_NAME}.azurecr.io"
                    sh "docker login -u ${env.REGISTRY_USERNAME} -p ${env.REGISTRY_PASSWORD} ${env.ACR_NAME}.azurecr.io"
                    echo "Pushing Docker image: ${env.IMAGE_NAME}"
                    sh "docker push ${env.IMAGE_NAME}"
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                // Use withAzureCli to handle Azure Service Principal
                withAzureCli(credentialsId: env.KUBE_CONFIG_CREDENTIALS, script: """
                    # Get the AKS credentials using Azure CLI
                    az aks get-credentials --resource-group ${env.RESOURCE_GROUP} --name ${env.AKS_CLUSTER_NAME} --file \$HOME/.kube/config
                    
                    # Apply Kubernetes manifests.  Consider applying all in the directory.
                    kubectl apply -f ${env.K8S_MANIFEST_PATH}/ -n ${env.NAMESPACE}
                    echo "Successfully deployed ${env.APP_NAME} to AKS namespace ${env.NAMESPACE}"
                """)
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    def serviceName = "${env.APP_NAME}-service"
                    def namespace = env.NAMESPACE
                    def maxRetries = 5
                    def retryInterval = 30

                    withCredentials([file(credentialsId: env.KUBE_CONFIG_CREDENTIALS, variable: 'KUBECONFIG_FILE')]) {
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
