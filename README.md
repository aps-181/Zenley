Add the required environmenet variables in your .env file
To access google calendar api, add the client_secret.json file 
Build the docker image - docker build -t zenley-slack-app . 
Run the container - docker run -it -p 5000:5000 zenley-slack-app