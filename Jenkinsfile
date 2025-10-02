pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "gangadhar369/myapp"
        DOCKER_TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                'git branch: 'main', url: 'https://github.com/gangadharpatil1595/flask-microservice.git'

            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE:$DOCKER_TAG .'
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-cred',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                       echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                       docker push $DOCKER_IMAGE:$DOCKER_TAG
                    """
                }
            }
        }
    }
}
