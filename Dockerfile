FROM intersystems/irishealth:2021.1.0.215.0
USER root

# Install basic tools
RUN apt-get update -yq \
    && apt-get -yq install curl gnupg ca-certificates \
    && curl -L https://deb.nodesource.com/setup_12.x | bash \
    && apt-get update -yq
RUN apt-get install -yq \
        ruby=1:2.5.* \
        ruby-dev=1:2.5.* \
        nodejs \
        python3 \
        git 
    # && npm --registry https://packages.simplifier.net install -g hl7.fhir.us.core-3.1.1 \
    # && npm --registry https://packages.simplifier.net install -g us.cdc.phinvads@0.7.0 \
    # && npm --registry https://packages.simplifier.net install -g hl7.fhir.us.carin-bb@1.1.0 \
    # && npm --registry https://packages.simplifier.net install -g hl7.fhir.us.immds@1.0.0 \
RUN npm install -g fhir-swagger
RUN mkdir -p /tmp/deps \
    && cd /tmp/deps \
    && wget -q https://pm.community.intersystems.com/packages/zpm/latest/installer -O zpm.xml
    # && iris session iris install \
RUN iris start $ISC_PACKAGE_INSTANCENAME quietly EmergencyId=sys,sys && \
    /bin/echo -e "sys\nsys\n" \
            " Do \$system.OBJ.Load(\"/tmp/deps/zpm.xml\", \"ck\")" \
            "zpm \"install fhir-openapi-gen\" " \
            " halt" \
    | iris session $ISC_PACKAGE_INSTANCENAME && \
    /bin/echo -e "sys\nsys\n" \
    | iris stop $ISC_PACKAGE_INSTANCENAME quietly
# COPY C:/Users/cduran/Documents/GitHub/fhir-openapi /data/fhir-openapi

RUN echo "SUCCESS"