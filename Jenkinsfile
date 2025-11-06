
pipeline {
    agent {
        kubernetes {
            inheritFrom 'flaskapp-agent'
            agentContainer 'jnlp'
            cloud 'Kubernetes'
            namespace 'cboc'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.9-slim
    command: [\'cat\']
    tty: true'''
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
                    mkdir -p reports
                    if [ -f tests/test_app.py ]; then
                    echo "Tests found — running pytest..."
                    export PYTHONPATH=$(pwd)
                    pytest -v --maxfail=1 --disable-warnings --junitxml=reports/test-results.xml
                else
                    echo "No tests found, skipping pytest..."
                    echo "<testsuite></testsuite>" > reports/test-results.xml
                fi
            '''
                }
            }
        }
        stage('Build podman Image') {
            steps {
                echo "Building podman image for ${env.APP_NAME}..."
                sh '''
                podman build -t myregistry.local/${APP_NAME}:latest .
                '''
            }
        }
        stage('Push Image to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'podmanhub-creds', usernameVariable: 'PODMAN_USER', passwordVariable: 'PODMAN_PASS')]) {
                    sh '''
                    echo "$PODMAN_PASS" | podman login -u "$PODMAN_USER" --password-stdin myregistry.local
                    podman push myregistry.local/${APP_NAME}:latest
                    '''
                }
            }
        }
        stage('Deploy to Dev Environment') {
            steps {
                echo "Deploying ${APP_NAME} to Dev environment..."
                sh '''
                oc set image deployment/${APP_NAME} ${APP_NAME}=myregistry.local/${APP_NAME}:latest -n dev || \
                oc set image deployment/${APP_NAME} ${APP_NAME}=myregistry.local/${APP_NAME}:latest -n dev
                '''
            }
        }
        post {
            always {
                echo "Pipeline finished (whether success or fail)."
                container('python') {
                    echo "Archiving reports..."
                    junit 'reports/test-results.xml'
                }
            }
            success {
                echo "Build, Test, and Deployment successful!"
            }
            failure {
                echo "Pipeline failed — check logs for details."
            }
        }
    }

        
        
    


        
