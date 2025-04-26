pipeline {
    agent any

    environment {
        REGISTRY = 'ranjeetchavan7.azurecr.io'
        IMAGE_NAME = 'simple-webapp'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', credentialsId: 'github-ssh', url: 'https://github.com/ranjeetchavan7/simple-webapp.git'
            }
        }

        stage('Azure CLI Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'my-aks-service-principal', usernameVariable: 'APP_ID', passwordVariable: 'APP_PASSWORD')]) {
                    echo 'Logging into Azure CLI using Service Principal Credentials'
                    sh '''
                        az logout || true
                        az login --service-principal -u $APP_ID -p $APP_PASSWORD --tenant 3c8ea0e4-127c-4a02-ac65-58830e4ac608
                    '''
                }
            }
        }

        stage('Build and Test') {
            steps {
                echo 'Building and testing the web app'
                sh '''
                    # Example: install requirements if Python
                    # pip install -r requirements.txt

                    # Example: run tests if any
                    # pytest tests/
                    echo "No unit tests configured. Skipping."
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker Image'
                sh '''
                    docker build -t $REGISTRY/$IMAGE_NAME:latest .
                '''
            }
        }

        stage('Push Docker Image to ACR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'acr-credentials', usernameVariable: 'ACR_USERNAME', passwordVariable: 'ACR_PASSWORD')]) {
                    sh '''
                        echo $ACR_PASSWORD | docker login $REGISTRY --username $ACR_USERNAME --password-stdin
                        docker push $REGISTRY/$IMAGE_NAME:latest
                    '''
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                echo 'Deploying to AKS Cluster'
                sh '''
                    az aks get-credentials --resource-group myResourceGroup --name myAKSCluster --overwrite-existing

                    kubectl set image deployment/simple-webapp simple-webapp=$REGISTRY/$IMAGE_NAME:latest --record
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                echo 'Verifying deployment on AKS'
                sh '''
                    kubectl rollout status deployment/simple-webapp
                    kubectl get pods
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully for webapp!'
        }
        failure {
            echo 'Pipeline failed for webapp :('
        }
    }
}
