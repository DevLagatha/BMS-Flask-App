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
    command: ['cat']
    tty: true
  - name: oc
    image: quay.io/openshift/origin-cli:4.12
    command: ['cat']
    tty: true
  - name: docker
    image: docker:24-cli     
    command: ['cat']
    tty: true
  - name: docker-image
    image: image-registry.openshift-image-registry.svc:5000/cboc/bms-flask-app:latest
    command: ['cat']
    tty: true

    
'''
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
                            echo "<testsuite></testsuite>" > /reports/test-results.xml
                        fi
                    '''

                }
            }
        }

        stage('Build Docker Image  ') 
        {
            steps {
                container('oc') 
                {

                echo "Building Docker image for ${env.APP_NAME}..."
                sh '''
                    oc start-build bms-flask-app --wait --follow -n cboc  
                    oc tag cboc/bms-flask-app:latest cboc/bms-flask-app:dep-tst -n cboc
                '''
                }
            }
        }


        stage('Push Image to Registry') {
            steps {
               withCredentials([usernamePassword(credentialsId: 'podmanhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                   sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin myregistry.local
                        docker push myregistry.local/bms-flask-app:latest
                   '''
                 }
            }
      }

        stage('Initializing Deployment to Dev Environment') {
            steps {
                echo "Deploying ${APP_NAME} to Dev environment..."
                sh '''
                    oc project cboc
                    oc set image deployment/bms-flask-app bms-flask-app=image-registry.openshift-image-registry.svc:5000/cboc/bms-flask-app:prod
                    oc rollout status deployment/bms-flask-app -n cboc
                '''
            }
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
