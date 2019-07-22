# nlab_harvester
**WIP**

A Harvester for nLab to generate the Harvests for MWS.
It takes the HTML-Files from [here](https://github.com/ncatlab/nlab-content-html)
docker-compose is used to bundle the harvester and a latexml daemon together
[MathWebSearch/latexml-mws-docker](https://github.com/MathWebSearch/latexml-mws-docker)
and [MathWebSearch/LaTeXML-plugin-iTeX2MML](https://github.com/MathWebSearch/LaTeXML-plugin-iTeX2MML)


# Usage
First create a docker volume for the harvestes
```bash
docker volume create harvests
```

Configuration is done through the env-variables in the docker-compose file
