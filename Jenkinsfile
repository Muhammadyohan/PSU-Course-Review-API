pipeline {
    agent any

    environment {
        WORKSPACE = pwd()
        SQLDB_URL="sqlite+aiosqlite:///./test-data/test-sqlalchemy.db"
        SECRET_KEY = "Kb4hybYaRhp0BMvA77l/JngifUb0u0e7kYhD3P+Xyig"
    }

    stages {
        stage('Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Muhammadyohan/PSU-Course-Review-API.git'
            }
        }

        stage('Test') {
            agent {
                docker {
                    image 'python:3.12'
                    reuseNode true
                    args '-u root'
                }
            }
            steps {

                sh "pip install poetry"
                sh "poetry install --with develop" 

                sh "poetry run pytest -v"
            }
        }

    }
}