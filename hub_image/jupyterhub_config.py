# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'

# launch with docker
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# we need the hub to listen on all ips when it is in a container
c.JupyterHub.hub_ip = '0.0.0.0'
# the hostname/ip that should be used to connect to the hub
# this is usually the hub container's name
c.JupyterHub.hub_connect_ip = 'a448hub_jan26'

# pick a docker image. This should have the same version of jupyterhub
# in it as our Hub.
c.DockerSpawner.image = 'phaustin/a448book:jan26'
c.DockerSpawner.image_whitelist = {'alison':'phaustin/alison:mar31',
                                   'andersen':'phaustin/andersen:feb10',
                                   'justin2':'phaustin/justin:mar21',
                                   'marjolein':'phaustin/a448book:jan26',
                                   'shuting':'phaustin/alison:feb10'}
notebook_dir = "/home/jovyan/work"
c.DockerSpawner.notebook_dir = notebook_dir

# tell the user containers to connect to our docker network
c.DockerSpawner.network_name = 'a448net_jan26'
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir,
                            "/home/phil/repos/a448hub/data_readonly": 
                            {"bind": '/home/jovyan/work/data_readonly', "mode": "ro"},
                            "/home/phil/repos/a448hub/data_share": 
                            {"bind": '/home/jovyan/work/data_share', "mode": "rw"}
                           }


# delete containers when the stop
c.DockerSpawner.remove = True
