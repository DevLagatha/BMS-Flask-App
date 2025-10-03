pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/DevLagatha/bms-flask-app.git'
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                python3 -m pip install --upgrade pip 
                pip install -r requirements.txt || true
                pip install pytest || true
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
            junit '**/test-results/*.xml' // collect test results if using pytest junit plugin
        }
        failure {
            echo "Tests failed!"
        }
        success {
            echo "All tests passed ✅"
        }
    }
}
