FROM intersystemsdc/irishealth-community
USER root

# Install basic tools
RUN apt-get update -yq \
    && apt-get -yq install curl gnupg ca-certificates \
    && curl -L https://deb.nodesource.com/setup_18.x | bash \
    && apt-get update -yq

RUN apt-get install -yq \
        ruby \
        ruby-dev \
        nodejs \
        python3 \
        git 
		
RUN npm install -g fhir-swagger

WORKDIR /opt/irisapp
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /opt/irisapp


USER ${ISC_PACKAGE_MGRUSER}

COPY src src
COPY module.xml module.xml
COPY iris.script iris.script

RUN iris start IRIS \
	&& iris session IRIS < iris.script \
    && iris stop IRIS quietly 

RUN echo "SUCCESS"