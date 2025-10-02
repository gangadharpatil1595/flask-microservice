pipeline {
    agent any

    environment {
        DOCKER_IMAGE   = "gangadhar369/flask-microservice"
        DOCKER_CRED_ID = "dockerhub-cred"      // your DockerHub credentials ID in Jenkins
        AWS_REGION     = "ap-south-1"
        K8S_NAMESPACE  = "flask-app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/gangadharpatil1595/flask-microservice.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                """
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CRED_ID}", usernameVariable: "USER", passwordVariable: "PASS")]) {
                    sh """
                        echo "$PASS" | docker login -u "$USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

       stage('Deploy to EKS') {
    steps {
        sh """
            # Update kubeconfig for EKS
            aws eks --region ${AWS_REGION} update-kubeconfig --name flask-eks

            # Safe redeploy (delete old, apply new)
            kubectl delete deployment flask-deployment -n ${K8S_NAMESPACE} --ignore-not-found
            kubectl apply -f /var/lib/jenkins/workspace/rest-api/k8s/ -n ${K8S_NAMESPACE}
            kubectl rollout status deployment/flask-deployment -n ${K8S_NAMESPACE}

            # Print LoadBalancer URL
            echo "-------------------------------------------------------"
            echo "Checking LoadBalancer Service External IP..."
            LB_URL=\$(kubectl get svc flask-service -n ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
            echo "Your Flask app is available at: http://$LB_URL"
            echo "-------------------------------------------------------"
        """
    }
}
