pipeline {
  agent any

  environment {
    DOCKER_USER       = 'gangadhar369'
    IMAGE_NAME        = 'flask-microservice'
    IMAGE_TAG         = "${env.BUILD_NUMBER}"
    AWS_REGION        = 'us-west-2'
    CLUSTER_NAME      = 'my-eks-cluster'
    RELEASE_NAME      = 'flask-app'
    NAMESPACE         = 'flask-app'
    KUBECONFIG        = "${WORKSPACE}/kubeconfig"
    DOCKER_CRED_ID    = 'dockerhub-creds'
    AWS_CRED_ID       = 'aws-creds'
    HELM_CHART_PATH   = './k8s'     // ✅ your Helm chart folder
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        echo "✅ Checked out branch: ${env.BRANCH_NAME}"
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

    stage('Push Docker Image to DockerHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${DOCKER_CRED_ID}", usernameVariable: 'DU', passwordVariable: 'DP')]) {
          sh '''
            echo ">>> Logging into DockerHub..."
            echo $DP | docker login -u $DU --password-stdin
            echo ">>> Pushing images..."
            docker push ${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}
            docker push ${DOCKER_USER}/${IMAGE_NAME}:latest
          '''
        }
      }
    }

    stage('Configure kubeconfig') {
      steps {
        withAWS(credentials: "${AWS_CRED_ID}", region: "${AWS_REGION}") {
          sh '''
            echo ">>> Setting up kubeconfig for EKS cluster..."
            aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME} --kubeconfig ${KUBECONFIG}
            export KUBECONFIG=${KUBECONFIG}
            kubectl get nodes
          '''
        }
      }
    }

    stage('Deploy using Helm') {
      steps {
        withAWS(credentials: "${AWS_CRED_ID}", region: "${AWS_REGION}") {
          sh '''
            echo ">>> Deploying Helm release to EKS..."
            export KUBECONFIG=${KUBECONFIG}
            cd ${WORKSPACE}
            helm upgrade --install ${RELEASE_NAME} ${HELM_CHART_PATH} \
              --namespace ${NAMESPACE} --create-namespace \
              --set image.repository=${DOCKER_USER}/${IMAGE_NAME} \
              --set image.tag=${IMAGE_TAG} \
              --wait --timeout 5m
          '''
        }
      }
    }

    stage('Post Deployment Check') {
      steps {
        withAWS(credentials: "${AWS_CRED_ID}", region: "${AWS_REGION}") {
          sh '''
            echo ">>> Verifying deployment..."
            export KUBECONFIG=${KUBECONFIG}
            kubectl get pods -n ${NAMESPACE}
            kubectl get svc -n ${NAMESPACE}
            helm list -n ${NAMESPACE}
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Helm deployment succeeded! Build: ${env.BUILD_NUMBER}"
    }

    failure {
      echo "❌ Build or deployment failed. Performing rollback..."
      withAWS(credentials: "${AWS_CRED_ID}", region: "${AWS_REGION}") {
        sh '''
          export KUBECONFIG=${KUBECONFIG}
          echo ">>> Rolling back Helm release..."
          helm rollback ${RELEASE_NAME} || echo "⚠️ Nothing to rollback yet."
        '''
      }
    }
  }
}
