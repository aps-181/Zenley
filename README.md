Add the required environmenet variables in your .env file

Create a folder db in your root directory before building the image to save your data

Build the docker image: docker build -t zenley-slack-app . 

To run the app: docker run -it -p 5000:5000 -v $(pwd)/db:/app/db zenley-slack-app
