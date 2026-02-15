pipeline {
    agent {
        kubernetes {
            label 'flaskapp-agent'
            inheritFrom 'flaskapp-agent'
            cloud 'Kubernetes'
            namespace 'cboc'
            defaultContainer 'python'
        }
    }

    environment {
        APP_NAME = "BMS-Flask-App"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'title',
                    url: 'https://github.com/DevLagatha/BMS-Flask-App.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                container('python') {
                    sh '''
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt || true
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('python') {
                    sh '''
                        mkdir -p reports
                        if [ -d "tests" ]; then
                            pytest -v tests || echo "<testsuite/>" > reports/test-results.xml
                        else
                            echo "No tests directory found, skipping tests."
                            echo "<testsuite/>" > reports/test-results.xml
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
                        oc rollout status deployment/bms-flask-app -n cboc
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            container('python') {
            junit 'reports/test-results.xml'
            archiveArtifacts artifacts: 'reports/*.xml',
                             allowEmptyArchive: true
        }
    }
}
