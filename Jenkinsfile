pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/<your-username>/bms-flask-app.git'
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                pip install -r requirements.txt
                pip install pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source venv/bin/activate
                pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }
    }

    post {
        always {
            junit '**/test-results.xml' // collect test results if using pytest junit plugin
        }
        failure {
            echo "Tests failed!"
        }
        success {
            echo "All tests passed ✅"
        }
    }
}
