# ROBOT_DEMO

Run sample robot suites to generate output.xml files

- Build the docker image

```
cd robotparser
docker build -t robotdemo:latest robotdemo.dockerfile
```

- Run the demo

```
  docker run --rm --name my_robotdemo \
   -v $(pwd):/app \
   robotdemo:latest ls -la /app

```
