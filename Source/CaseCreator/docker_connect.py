# this code will connect to the docker container and execute the command
# and return the output
import docker

def connect_docker_container(container_name, command):
    client = docker.from_env()
    container = client.containers.get(container_name)
    output = container.exec_run(command)
    return output

def list_all_containers():
    client = docker.from_env()
    return client.containers.list(all=True)

def list_all_images():
    client = docker.from_env()
    return client.images.list()

def run_image(image_name, command):
    client = docker.from_env()
    container = client.containers.run(image_name, command, detach=True)
    return container

def main():
    #print(list_all_containers())
    images = list_all_images()
    print(run_image(images[0], 'ls'))
    #print(connect_docker_container('mycontainer', 'ls'))

if __name__ == '__main__':
    main()