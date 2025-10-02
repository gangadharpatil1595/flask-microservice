pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "gangadhar369/flask-microservice"
        AWS_REGION   = "ap-south-1"
        K8S_NAMESPACE = "flask-app"
        DOCKER_CREDENTIALS_ID = "dockerhub-cred"   // <-- your DockerHub Jenkins credential ID
        AWS_CREDENTIALS_ID    = "aws-cred"        // <-- your AWS Jenkins credential ID
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/gangadharpatil1595/flask-microservice.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${env.BUILD_NUMBER}
                        docker tag ${DOCKER_IMAGE}:${env.BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withAWS(region: "${AWS_REGION}", credentials: "${AWS_CREDENTIALS_ID}") {
                    sh """
                        aws eks update-kubeconfig --region ${AWS_REGION} --name flask-eks
                        kubectl apply -f k8s/ -n ${K8S_NAMESPACE}
                        kubectl rollout status deployment/flask-deployment -n ${K8S_NAMESPACE}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful! Your Flask app is live on EKS"
        }
        failure {
            echo "Deployment failed. Please check logs."
        }
    }
}
