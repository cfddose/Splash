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

def run_container(image_name, command=None, mount_dir="/home/" ,container_name=None, detach=True):
    """Runs a Docker container with the specified image and command."""
    client = docker.from_env()
    
    cmd = f"/bin/bash -c 'source /usr/lib/openfoam/openfoam2406/etc/bashrc && {command} && exec /bin/bash'"
    
    try:
        container = client.containers.run(
            image=image_name,
            command=cmd,
            name=container_name,
            detach=detach,
            tty=True,
            stdin_open=True,
            volumes={mount_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir='/app'
        )
        print(f"Container {container.id} started successfully.")
        # Stream logs in real-time
        #for line in container.logs(stream=True):
        #    print(line)

        return container
    except docker.errors.APIError as e:
        print(f"Error: {e}")
        return None


def main():
    #print(list_all_containers())
    images = list_all_images()
    print(images)
    print(run_image(images[0], 'ls'))
    #print(connect_docker_container('mycontainer', 'ls'))

if __name__ == "__main__":
    image = "thawtar1990/of2406:latest"  # Change to your desired image
    #command = "/bin/bash -c 'blockMesh && exec /bin/bash'"  # Change to your command
    command = "blockMesh && simpleFoam"  # Change to your command
    mount_dir = "/Users/thawtar/Desktop/Work/03_Splash/02_Run/channel"
    container = run_container(image, command, mount_dir)
    
    
    if container:
        print("Logs:")
        print(container.logs().decode('utf-8'))

    main()