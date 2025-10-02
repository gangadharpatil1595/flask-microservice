pipeline {
    agent any

    environment {
        DOCKER_IMAGE   = "gangadhar369/flask-microservice"
        DOCKER_TAG     = "${BUILD_NUMBER}"
        AWS_REGION     = "ap-south-1"
        K8S_NAMESPACE  = "flask-app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/gangadharpatil1595/flask-microservice.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                   docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                   docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-cred',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                       echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                       docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                       docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh """
                   aws eks --region ${AWS_REGION} update-kubeconfig --name flask-eks
                   kubectl apply -f k8s/ -n ${K8S_NAMESPACE}
                   kubectl rollout status deployment/flask-deployment -n ${K8S_NAMESPACE}
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -af || true'
        }
    }
}
