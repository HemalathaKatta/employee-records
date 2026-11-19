pipeline {
    agent any

    // These boxes appear when you click "Build with Parameters"
    parameters {
        string(name: 'NAME',   defaultValue: '', description: 'Employee name, e.g. Ravi Kumar')
        string(name: 'EMP_ID', defaultValue: '', description: 'Employee ID, e.g. EMP1011')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Downloading the latest employees.xlsx from GitHub...'
                checkout scm
            }
        }

        stage('Add Employee') {
            steps {
                echo "Adding: ${params.NAME} (${params.EMP_ID})"
                sh 'python3 add_employee.py --file employees.xlsx --name "$NAME" --empid "$EMP_ID"'
            }
        }

        stage('Push to GitHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-token',
                                                  usernameVariable: 'GIT_USER',
                                                  passwordVariable: 'GIT_TOKEN')]) {
                    sh '''
                        git config user.name "Jenkins"
                        git config user.email "jenkins@localhost"
                        git add employees.xlsx
                        if git diff --cached --quiet; then
                            echo "No change - nothing to upload"
                        else
                            git commit -m "Jenkins: add employee $EMP_ID (build $BUILD_NUMBER)"
                            REPO=$(git config remote.origin.url | sed 's#https://##')
                            git pull --rebase "https://$GIT_USER:$GIT_TOKEN@$REPO" main
                            git push "https://$GIT_USER:$GIT_TOKEN@$REPO" HEAD:main
                            echo "employees.xlsx updated on GitHub"
                        fi
                    '''
                }
            }
        }

        stage('Copy to Local') {
            steps {
                sh '''
                    if [ -d /data ]; then
                        cp employees.xlsx /data/employees.xlsx
                        echo "employees.xlsx copied to C:\\jenkins-data on the laptop"
                    else
                        echo "Shared folder /data not found - skipped local copy"
                    fi
                '''
            }
        }
    }

    post {
        success { echo 'PIPELINE PASSED' }
        failure { echo 'PIPELINE FAILED: check the error above' }
    }
}
