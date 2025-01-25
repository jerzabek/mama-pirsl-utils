# mama-pirsl-utils

A repository with scripting utils for mama pirsl

Scripts are available through command line interface as well as through a web interface.

## Command line interface

CLI installation is described in [photo_processing_script/README.md](photo_processing_script/README.md).

## Web interface

Web interface is containerized using Docker. The interface is a single `index.html` file served through an nginx container. API calls are routed to the appropriate Docker container inside of the `nginx.conf` file.

### Usage

Run the docker compose file:

```bash
docker compose up -d
```

Access the interface through [http://localhost:1234](http://localhost:1234).
