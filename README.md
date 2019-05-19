# kinesiologiapp-backend
## Run the server
First create a new folder:
```
mkdir kinesio
```

Here we will have folders for the database, the logs and the source code.

Now clone the source code from this repository:
```
git clone https://github.com/LucasEsposito/kinesiologiapp-backend
```

Go to the new folder "kinesiologiapp-backend" (the project's root folder) and get the containers up:
```
cd kinesiologiapp-backend
sudo docker-compose up -d
```

Your server instance should be running at http://127.0.0.1:80

If it's not running, check the containers' status:
```
sudo docker-compose ps
```

and the logs with the following command:
```
cat ../syslog/messages
```
