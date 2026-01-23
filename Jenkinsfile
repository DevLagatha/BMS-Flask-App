pipeline {
    agent {
        kubernetes {
            label 'flaskapp-agent'
            cloud 'Kubernetes'
            namespace 'cboc'
            defaultContainer 'python'

            yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: controller-oa
  containers:
  - name: python
    image: python:3.9-slim
    command: ['cat']
    tty: true
  - name: oc
    image: quay.io/openshift/origin-cli:4.12
    command: ['cat']
    tty: true
"""
        }
    }

    environment {
        APP_NAME = "BMS-Flask-App"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                git branch: 'main',
                    url: 'https://github.com/DevLagatha/BMS-Flask-App.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh '''
                        python -m pip install --upgrade pip
                        if [ -f requirements.txt ]; then
                            pip install -r requirements.txt
                        else
                            echo "No requirements.txt found"
                        fi
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('python') {
                    sh '''
                        mkdir -p reports
                        if [ -f tests/test_app.py ]; then
                            export PYTHONPATH=$(pwd)
                            pytest -v tests/test_app.py \
                                   --maxfail=1 \
                                   --disable-warnings \
                                   --junitxml=reports/test-results.xml
                        else
                            echo "<testsuite></testsuite>" > reports/test-results.xml
                        fi
                    '''
                }
            }
        }

        stage('Build Image') {
            steps {
                container('oc') {
                    sh '''
                        oc start-build bms-flask-app --wait --follow -n cboc
                        oc tag cboc/bms-flask-app:latest cboc/bms-flask-app:prod -n cboc
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                container('oc') {
                    sh '''
                        oc set image deployment/bms-flask-app \
                          bms-flask-app=image-registry.openshift-image-registry.svc:5000/cboc/bms-flask-app:prod \
                          -n cboc
                        oc rollout status deployment/bms-flask-app -n cboc
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            script {
                if (env.WORKSPACE) {
                    container('python') {
                        archiveArtifacts artifacts: 'reports/test-results.xml', allowEmptyArchive: true
                        junit 'reports/test-results.xml'
                    }
                } else {
                    echo 'Skipping post actions: no workspace allocated'
                }
            }
        }

        success {
            echo 'Build, test, and deployment succeeded.'
        }

        failure {
            echo 'Pipeline failed. Check logs.'
        }
    }
}
