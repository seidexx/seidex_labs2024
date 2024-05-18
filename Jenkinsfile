pipeline {
    agent any

    stages {
        stage('Start') {
            steps {
                echo 'Lab_2: started by GitHub'
            }
        }

        stage('Image build') {
            steps {
                sh "docker build -t seidex_labs2024:latest ."
                sh "docker tag seidex_labs2024 seidexx/seidex_labs2024:latest"
                sh "docker tag seidex_labs2024 seidexx/seidex_labs2024:$BUILD_NUMBER"
            }
        }

        stage('Push to registry') {
            steps {
                withDockerRegistry([ credentialsId: "dockerhub_token", url: "" ])
                {
                    sh "docker push seidexx/seidex_labs2024:latest"
                    sh "docker push seidexx/seidex_labs2024:$BUILD_NUMBER"
                }
            }
        }

        stage('Deploy image'){
            steps{
                sh "docker stop \$(docker ps -q) || true"
                sh "docker container prune --force"
                sh "docker image prune --force"
                //sh "docker rmi \$(docker images -q) || true"
                sh "docker run -d -p 80:80 seidexx/seidex_labs2024"
            }
        }
    }   
}
