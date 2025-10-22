pipeline {
    agent { label flaskapp-agent }

    stages {
        stage('Check Agent Connection') {
            steps {
                echo "Testing Jenkins agent connection..."
                sh '''
                    echo "Agent is working properly!"
                    hostname
                    whoami
                    python3 --version || echo "Python not found"
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished (whether success or fail)."
        }
    }
}
