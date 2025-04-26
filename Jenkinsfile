pipeline {
    agent any

    environment {
        // Credentials IDs in Jenkins
        GIT_CREDENTIALS = 'github-ssh'
        // Other environment variables
        ACR_NAME = 'ranjeet'
        IMAGE_NAME = "${ACR_NAME}.azurecr.io/webapp:${BUILD_ID}"
        KUBE_CONFIG_CREDENTIALS = 'my-aks-service-principal'  // Corrected credential ID
        DEPLOYMENT_NAME = 'webapp-deployment'
        NAMESPACE = 'default'
        DOCKERFILE_PATH = 'webapp'
        K8S_MANIFEST_PATH = 'k8s'
        APP_NAME = 'webapp'
        REGISTRY_CREDENTIALS = 'acr-credentials'
        RESOURCE_GROUP = 'your-resource-group'  // Replace with your actual resource group
        AKS_CLUSTER_NAME = 'your-aks-cluster'    // Replace with your actual AKS cluster name
    }

    stages {
        stage('Checkout') {
            steps {
                // Use credentialsId for Git, and specify the branch
                git credentialsId: env.GIT_CREDENTIALS,
                    url: 'https://github.com/ranjeetchavan7/simple-webapp.git',
                    branch: 'main'
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
                script {
                    withCredentials([usernamePassword(credentialsId: env.REGISTRY_CREDENTIALS,
                                                      passwordVariable: 'REGISTRY_PASSWORD',
                                                      usernameVariable: 'REGISTRY_USERNAME')]) {
                        echo "Building Docker image: ${env.IMAGE_NAME}"
                        // Changed context to "." and added a tag
                        sh "docker build -f Dockerfile -t ${env.APP_NAME} ."
                        sh "docker tag ${env.APP_NAME} ${env.IMAGE_NAME}"
                        echo "Logging into Azure Container Registry: ${env.ACR_NAME}.azurecr.io"
                        sh "docker login -u \$REGISTRY_USERNAME -p \$REGISTRY_PASSWORD ${env.ACR_NAME}.azurecr.io"
                        echo "Pushing Docker image: ${env.IMAGE_NAME}"
                        sh "docker push ${IMAGE_NAME}"
                    }
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                // Use withAzureCli to handle Azure Service Principal
                withAzureCli(credentialsId: env.KUBE_CONFIG_CREDENTIALS) {
                    script {
                        echo "Deploying to AKS"
                        // Get the AKS credentials using Azure CLI.  Assumes your SP has the necessary permissions.
                        sh "az aks get-credentials --resource-group ${env.RESOURCE_GROUP} --name ${env.AKS_CLUSTER_NAME} --overwrite"

                        // Apply Kubernetes manifests
                        sh "kubectl apply -f ${env.K8S_MANIFEST_PATH}/deployment.yaml -n ${env.NAMESPACE}"
                        sh "kubectl apply -f ${env.K8S_MANIFEST_PATH}/service.yaml -n ${env.NAMESPACE}"
                        echo "Successfully deployed ${env.APP_NAME} to AKS namespace ${env.NAMESPACE}"
                    }
                }
            }
        }
    }
}
