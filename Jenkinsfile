pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'seidexx/seidex_labs2024'
    }

    stages {
        stage('Start') {
            steps {
                echo 'Lab_4: start for monitoring'
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                    telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

        stage('Image build') {
            steps {
                sh "docker build -t seidex_labs2024:latest ."
                sh "docker tag seidex_labs2024 $DOCKER_IMAGE:latest"
                sh "docker tag seidex_labs2024 $DOCKER_IMAGE:$BUILD_NUMBER"
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                    telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

        stage('Push to registry') {
            steps {
                withDockerRegistry([ credentialsId: "dockerhub_token", url: "" ])
                {
                    sh "docker push $DOCKER_IMAGE:latest"
                    sh "docker push $DOCKER_IMAGE:$BUILD_NUMBER"
                }
            }
            post{
                failure {
                    script {
                    // Send Telegram notification on success
                    telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }

        stage('Deploy image'){
            steps{
                sh "docker stop \$(docker ps | grep '$DOCKER_IMAGE' | awk '{print \$1}') || true"
                sh "docker container prune --force"
                sh "docker image prune --force"
                //sh "docker rmi \$(docker images -q) || true"
                sh "docker run -d -p 80:80 $DOCKER_IMAGE"
            }

            post{
                failure {
                    script {
                    // Send Telegram notification on success
                    telegramSend message: "Job Name: ${env.JOB_NAME}\nBranch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}\nFailure stage: '${env.STAGE_NAME}'"
                    }
                }
            }
        }
    }   
        

    post {
        success {
            script {
                // Send Telegram notification on success
                telegramSend message: "Job Name: ${env.JOB_NAME}\n Branch: ${env.GIT_BRANCH}\nBuild #${env.BUILD_NUMBER}: ${currentBuild.currentResult}"
            }
        }
    }

}
