pipeline {
    agent any

    environment {
        // Credentials IDs in Jenkins
        REGISTRY_CREDENTIALS = 'acr-credentials'
        KUBE_CONFIG_CREDENTIALS = 'my-aks-service-principal'
        GIT_CREDENTIALS = 'github-ssh'

        // Azure Container Registry details
        ACR_NAME = 'ranjeet'
        IMAGE_NAME = "${ACR_NAME}.azurecr.io/webapp:${BUILD_ID}"

        // Kubernetes deployment details
        DEPLOYMENT_NAME = 'webapp-deployment'
        NAMESPACE = 'default'

        // Project paths
        DOCKERFILE_PATH = 'webapp'
        K8S_MANIFEST_PATH = 'k8s'
        APP_NAME = 'webapp' // Added for consistency
    }

    stages {
        stage('Checkout') {
            steps {
                // Use credentialsId for Git
                git credentialsId: env.GIT_CREDENTIALS, url: 'https://github.com/ranjeetchavan7/simple-webapp.git'
            }
        }

        stage('Build and Test') {
            steps {
                script {
                    echo "Setting up virtual environment and installing dependencies for ${env.APP_NAME}"
                    sh 'python -m venv venv'
                    sh 'source venv/bin/activate'
                    sh "pip install -r ${env.DOCKERFILE_PATH}/requirements.txt"

                    echo "Running tests for ${env.APP_NAME}"
                    // Check if tests directory exists before running tests
                    if (fileExists("${env.DOCKERFILE_PATH}/tests")) {
                        sh "python -m unittest discover ${env.DOCKERFILE_PATH}/tests"
                    } else {
                        echo "No tests directory found in ${env.DOCKERFILE_PATH}. Skipping tests."
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS,
                                                passwordVariable: 'REGISTRY_PASSWORD',
                                                usernameVariable: 'REGISTRY_USERNAME')]) {
                    echo "Building Docker image: ${env.IMAGE_NAME}"
                    // Explicitly define build context and Dockerfile path
                    sh "docker build -f ${env.DOCKERFILE_PATH}/Dockerfile -t ${env.APP_NAME} ${env.DOCKERFILE_PATH}"
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
                withCredentials([file(credentialsId: env.KUBE_CONFIG_CREDENTIALS,
                                      variable: 'KUBECONFIG_FILE')]) {
                    echo "Applying Kubernetes manifests from ${env.K8S_MANIFEST_PATH} to namespace ${env.NAMESPACE}"
                    sh "kubectl --kubeconfig=\"${KUBECONFIG_FILE}\" apply -f ${env.K8S_MANIFEST_PATH}/deployment.yaml -n ${env.NAMESPACE}"
                    sh "kubectl --kubeconfig=\"${KUBECONFIG_FILE}\" apply -f ${env.K8S_MANIFEST_PATH}/service.yaml -n ${env.NAMESPACE}"
                    echo "Successfully deployed ${env.APP_NAME} to AKS namespace ${env.NAMESPACE}"
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    def serviceName = "${env.APP_NAME}-service" // Consistent naming
                    def namespace = env.NAMESPACE
                    def maxRetries = 5
                    def retryInterval = 30

                    withCredentials([file(credentialsId: env.KUBE_CONFIG_CREDENTIALS, variable: 'KUBECONFIG_FILE')]) {
                        for (int i = 0; i < maxRetries; i++) {
                            try {
                                // Use jsonpath to extract the IP, handle null
                                def serviceInfo = sh(
                                    script: "kubectl --kubeconfig=\"${KUBECONFIG_FILE}\" get service ${serviceName} -n ${namespace} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'",
                                    returnStdout: true
                                ).trim()

                                if (serviceInfo) {
                                    echo "Service ${serviceName} is available at: ${serviceInfo}"
                                    // Add a basic HTTP check (requires curl or similar in the Docker image)
                                    sh "curl --fail --show-error http://${serviceInfo}" //check status
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
