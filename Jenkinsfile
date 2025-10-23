pipeline {
    agent {
        kubernetes {
            inheritFrom 'flaskapp-agent'
        }
    }

    environment {
        APP_NAME = "BMS-Flask-App"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                git branch: 'main', url: 'https://github.com/DevLagatha/BMS-Flask-App.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                container('python') {
                    echo "Installing Python dependencies..."
                    sh '''
                        pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            echo "No requirements.txt found, skipping..."
                        fi
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('python') {
                    echo "Running unit tests..."
                    sh '''
                        if [ -f tests/test_app.py ]; then
                            pytest -v --maxfail=1 --disable-warnings
                        else
                            echo "No tests found, skipping..."
                        fi
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image for ${env.APP_NAME}..."
                sh '''
                    docker build -t myregistry.local/${APP_NAME}:latest .
                '''
            }
        }

        stage('Push Image to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin myregistry.local
                        docker push myregistry.local/${APP_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                echo "Deploying ${APP_NAME} to Dev environment..."
                sh '''
                    # For OpenShift/Kubernetes deployment
                    oc set image deployment/${APP_NAME} ${APP_NAME}=myregistry.local/${APP_NAME}:latest -n dev || \
                    kubectl set image deployment/${APP_NAME} ${APP_NAME}=myregistry.local/${APP_NAME}:latest -n dev
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished (whether success or fail)."
            archiveArtifacts artifacts: 'build/libs/**/*.jar', fingerprint: true
            junit 'build/reports/**/*.xml'
        }
        success {
            echo "Build, Test, and Deployment successful!"
        }
        failure {
            echo "Pipeline failed — check logs for details."
        }
    }
}
