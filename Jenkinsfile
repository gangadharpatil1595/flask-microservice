pipeline {
  agent any

  environment {
    DOCKERHUB_CRED_ID = 'dockerhub-creds'
    AWS_CRED_ID       = 'aws-creds'
    AWS_REGION        = 'us-west-2'
    CLUSTER_NAME      = 'my-eks-cluster'
    DOCKER_USER       = 'gangadhar369'
    IMAGE_NAME        = 'flask-microservice'
    IMAGE_TAG         = "${env.BUILD_NUMBER}"
    K8S_DIR           = 'k8s'
    NAMESPACE         = 'flask-app'
    KUBECONFIG        = "${WORKSPACE}/kubeconfig"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        echo "Commit: ${env.GIT_COMMIT}"
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          echo ">>> Building Docker image..."
          docker build -t ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG} .
          docker tag ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_USER}/${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Push Docker Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: env.DOCKERHUB_CRED_ID, usernameVariable: 'DU', passwordVariable: 'DP')]) {
          sh '''
            echo ">>> Logging in to DockerHub..."
            echo $DP | docker login -u $DU --password-stdin
            echo ">>> Pushing Docker images..."
            docker push ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
            docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
          '''
        }
      }
    }

    stage('Configure kubeconfig') {
      steps {
        withAWS(credentials: env.AWS_CRED_ID, region: env.AWS_REGION) {
          sh '''
            echo ">>> Setting up kubeconfig for EKS cluster"
            aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME} --kubeconfig ${KUBECONFIG}
            export KUBECONFIG=${KUBECONFIG}
            kubectl get nodes
          '''
        }
      }
    }

    stage('Update K8s Manifests with New Image') {
      steps {
        script {
          sh '''
            echo ">>> Updating manifests with new image tag..."
            mkdir -p ${K8S_DIR}
            if [ ! -f ${K8S_DIR}/deployment.yaml ]; then
              echo ">>> Creating default deployment manifest..."
              cat <<EOF > ${K8S_DIR}/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-microservice
  labels:
    app: flask-microservice
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-microservice
  template:
    metadata:
      labels:
        app: flask-microservice
    spec:
      containers:
      - name: flask-microservice
        image: ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
        ports:
        - containerPort: 5000
EOF
            fi

            # Service manifest
            if [ ! -f ${K8S_DIR}/service.yaml ]; then
              cat <<EOF > ${K8S_DIR}/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  selector:
    app: flask-microservice
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
EOF
            fi
          '''
        }
      }
    }

    stage('Deploy to EKS') {
      steps {
        withAWS(credentials: env.AWS_CRED_ID, region: env.AWS_REGION) {
          sh '''
            export KUBECONFIG=${KUBECONFIG}
            kubectl get ns ${NAMESPACE} || kubectl create ns ${NAMESPACE}
            echo ">>> Deploying application to EKS..."
            kubectl apply -f ${K8S_DIR}/deployment.yaml -n ${NAMESPACE}
            kubectl apply -f ${K8S_DIR}/service.yaml -n ${NAMESPACE}
          '''
        }
      }
    }

    stage('Smoke Test') {
      steps {
        withAWS(credentials: env.AWS_CRED_ID, region: env.AWS_REGION) {
          sh '''
            echo ">>> Waiting for pods to be ready..."
            export KUBECONFIG=${KUBECONFIG}
            kubectl rollout status deployment/flask-microservice -n ${NAMESPACE} --timeout=180s
            kubectl get svc -n ${NAMESPACE}
            echo "✅ Deployment successful and service available!"
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Deployment succeeded for build ${env.BUILD_NUMBER}"
    }
    failure {
      echo "❌ Deployment failed. Check Jenkins logs for details."
    }
  }
}
