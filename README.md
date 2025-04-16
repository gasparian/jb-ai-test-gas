# Environment Setuper

First, check out setuper cli tool details in the [env-setuper](./env-setuper/) project folder.  

Here are 3 projects I was using for testing the tool:  
  - `python-mnist` - simple pytorch program to train CNN on Mnist data;  
  - `rust_web_service` - a simple rust hello world http server;  
  - `rust_web_service_f` - the same rust service, but with an error inside: `hello_world` handler can't be imported, since it's in a main file;  

So the expected outcome - successfull setup for the first two projects, and warning with suggestion to the final one.  

You can test them by running `env-setuper` against each of these folders.  

## Docker 

In order to run more complex tests, it's worth to add an isolation level - containers.  
We can start from the Ubuntu with minimal setup, and then ask setuper to setup a project.  
In a [Dockerfile](./Dockerfile) you can find that I've copied those predefined projects inside the docker, to experiment with them.  
You can copy your projects to the running container just via `docker cp`.  

First, use the instructions from `env_setuper` project, and build the package with `make build`.  

Then, build the docker image:  
```sh
docker compose build
```  

And run it: 
```sh
OPENAI_API_KEY=$OPENAI_API_KEY docker compose run app
```  

For `arm` macs:
```sh
OPENAI_API_KEY=$OPENAI_API_KEY DOCKER_PLATFORM=linux/arm64 docker compose run app
```

You'll see the interactive shell, `env-setuper` will be already installed there, so you can run it, with non-restricted shell mode:  
```sh
env-setuper ./python-mnist --no-restricted-shell
```  
```sh
env-setuper ./python-mnist --no-restricted-shell --max-agent-iter 50
```
