#! /usr/bin/bash

# TODO ask for variables ahead of time

# Execute Docker Build
echo "Would you like to build the IRIS w/ Python Image? (y/n)"
read answer
if [ "$answer" == "y" ]; then
    echo "Path to Dockerfile?"
    echo "(Press Enter For current directory: $PWD)"
    read dockerfilepath
    until [ -d "$dockerfilepath" ] || [ -z "$dockerfilepath" ]; do
        echo "couldn't find path ${dockerfilepath}.. Please try again."
        echo "Path to Dockerfile?"
        echo "(Press Enter For current directory: $PWD)"
        read dockerfilepath
    done
    if [ -z "$dockerfilepath" ]; then
        docker build -t "intersystems/iriswpython:1.2.0" .
    else
        docker build -t "intersystems/iriswpython:1.2.0" $dockerfilepath
    fi
    echo "Built a new image with necessary dependencies tagged intersystems/iriswpython:1.2.0"
fi
# Execute compose-up for IAM + IRIS
echo "Would you like to launch the IRIS w/ Python container? (y/n)"

read answer

if [ "$answer" == "y" ]; then
    echo "Path to docker-compose file?"
    echo "(Press Enter For current directory: $PWD)"
    read iriscomposepath
    until [ -d "$iriscomposepath" ] || [ -z "$iriscomposepath" ]; do
        echo "couldn't find path ${iriscomposepath}.. Please try again."
        echo "Path to docker-compose file?"
        echo "(Press Enter For current directory: $PWD)"
        read iriscomposepath
    done
    if [ -z "$iriscomposepath" ]; then
        docker-compose up -d
    else
        cd $iriscomposepath
        docker-compose up -d
    fi
    echo "Launched IRIS w/ Python Container"
fi
echo "Would you like to launch the IAM Container? (y/n)"
cd $PWD

read answer

if [ "$answer" == "y" ]; then
    echo "Path to docker-compose file?"
    echo "(Press Enter For current directory: $PWD)"
    read iamcomposepath
    until [ -d "$iamcomposepath" ] || [ -z "$iamcomposepath" ]; do
        echo "couldn't find path ${iamcomposepath}.. Please try again."
        echo "Path to docker-compose file?"
        echo "(Press Enter For current directory: $PWD)"
        read iamcomposepath
    done
    until [[ "$correct" =~ ^[Yy] ]] || [[ "$correct" =~ ^[Yy][Ee][Ss] ]]; do

        echo "Enter the full image repository, name and tag for your IAM docker image: "
        echo "(Return for the default iam image: intersystems/iam:2.3.3.2-1)"
        read image
        image="${image:=intersystems/iam:2.3.3.2-1}"
        echo 'Enter the IP address for your InterSystems IRIS instance. The IP address has to be accessible from within the IAM container, therefore, do not use "localhost" or "127.0.0.1" if IRIS is running on your local machine. Instead use the IP address of your local machine. If IRIS is running in a container, use the IP address of the host environment, not the IP address of the IRIS container: '
        read ip
        hostip=$ip
        echo "Enter the web server port for your InterSystems IRIS instance: "
        read port
        while true; do
            echo "Enter the password for the IAM user for your InterSystems IRIS instance: "
            read -s pass1
            echo "Re-enter your password: "
            read -s pass2
            if [ "$pass1" = "$pass2" ]
            then break
            else echo "Passwords don't match."
            fi
        done

        echo 'If local policy requires that HTTPS be used for communication, please provide the full path to your CA Certificate file now. Otherwise hit "Return": '
        read cacertpath

        echo 'If your InterSystems IRIS instance is only accessible via its CSPConfigName URL prefix, please provide the prefix with a trailing slash (/) now. Otherwise hit "Return": '
        read pathprefix

        echo ""
        echo "Your inputs are:"
        echo "Full image repository, name and tag for your IAM docker image: $image"
        echo "IP address for your InterSystems IRIS instance: $ip"
        echo "Web server port for your InterSystems IRIS instance: $port" 
        echo "CA Certificate for HTTPS: $cacertpath"
        echo "CSPConfigName URL prefix: $pathprefix"

        while true; do
            echo "Would you like to continue with these inputs (y/n)? "
            read correct
            case $correct in
                [Yy] | [Yy][Ee][Ss] | [Nn] | [Nn][Oo]) break;;
                * ) echo "Please answer yes or no";;
            esac
        done
    done
    ISC_IAM_IMAGE=$image
    ISC_IRIS_URL="http://IAM:$pass1@$ip:$port/${pathprefix}api/iam/license"
    if [[ -z "${cacertpath}" ]]; then
        irisurl="http://$ip:$port/${pathprefix}api/iam/license"
        keyresponse=$(curl -s -i -w '%{response_code}' -o /dev/null --max-time 7 -u IAM:$pass1 $irisurl)
    else
        irisurl="https://$ip:$port/${pathprefix}api/iam/license"
        keyresponse=$(curl -s -i -w '%{response_code}' -o /dev/null --max-time 7 -u IAM:$pass1 --cacert ${cacertpath} $irisurl)
    fi
    if [ "$keyresponse" -ge "500" ]; then  
        echo "Internal server error when testing inputs."
        echo "Return to exit"
        read exiting
        exit 1
    elif [ "$keyresponse" -eq "404" ]; then
        echo "The /api/iam web application is disabled. Please enable it before running this script again."
        echo "Return to exit"
        read exiting
        exit 1
    elif [ "$keyresponse" -eq "401" ]; then
        echo "Authorization failed. Please make sure to enable the IAM user and reset its password before running this script again. This error may also mean that you entered the wrong password to this script."
        echo "Return to exit"
        read exiting
        exit 1
    elif [ "$keyresponse" -eq "400" ]; then
        echo "Request failed with a 400 status code. You may be trying to use HTTP on an SSL-enabled server port."
        echo "Return to exit"
        read exiting
        exit 1
    elif [ "$keyresponse" -eq "204" ]; then
        echo "No content. Either your InterSystems IRIS instance is unlicensed or your license key does not contain an IAM license."
        echo "Return to exit"
        read exiting
        exit 1
    elif [ "$keyresponse" -eq "000" ]; then
        echo "Couldn't reach InterSystems IRIS at $ip:$port. One or both of your IP and Port are incorrect."
        echo "Return to exit"
        read exiting
        exit 1
    else 
        echo "Successfully acquired IAM license"
    fi
    if [ -z "$iamcomposepath" ]; then
        docker-compose up -d
    else
        cd $iamcomposepath
        docker-compose up -d
    fi
    echo "Launched IAM Container"
fi
# Execute preprocess + Process
cd $PWD
echo "Would you like to initiate the FHIR OpenAPI Generator Process? (y/n)"

read answer
if [ "$answer" == "y" ]; then
    echo "Please enter your FHIR Server Path (Ex: http://<IAM IP>:8000/r4)"
    read fhirserverpath
    echo "Please enter your IRIS Namespace (Press enter for Default: USER)"
    read namespace
    namespace="${namespace:=USER}"
    echo "Please enter the name of the FHIR Package you wish to use (Press enter for Default: FHIRr4)"
    read fhirpackage
    # docker exec -i -e fhirserverpath=$fhirserverpath -e namespace=$namespace -e fhirpackage=$fhirpackage i4hcontainer_iris_1 bash < ./fhir-openapi-script.sh
    docker exec -i \
        -e fhirserverpath=$fhirserverpath \
        -e namespace=$namespace \
        -e fhirpackage=$fhirpackage \
        i4hcontainer_iris_1 bash -c 'echo -e "superuser\nnew\ndo ##class(FHIROpenAPI.Generator).Preprocess()\n${fhirserverpath}\n${namespace}\n${fhirpackage}\n0\nh" |iris session iris'

    docker exec -i i4hcontainer_iris_1 \
        bash -c 'echo -e "superuser\nnew\ns ^FHIRSavePath=\"/data\"\ndo ##class(FHIROpenAPI.Generator).Run()\nh" |iris session iris'
    
    echo 'Created Spec successfully'
fi

# Posting to IAM
echo "Would you like to post the FHIR Spec to IAM? (y/n)"

read answer
if [ "$answer" == "y" ]; then
    echo 'Enter the IP address for your IAM instance. The IP address has to be accessible from within the IAM container, therefore, do not use "localhost" or "127.0.0.1" if IRIS is running on your local machine. Instead use the IP address of your local machine. If IRIS is running in a container, use the IP address of the host environment, not the IP address of the IRIS container: '
    if [ -n "$hostip" ]; then
        echo "(Return to use the previous IP address: ${hostip})"
    fi
    read ip
    if [ -z "$ip" ] && [ -n "$hostip" ]; then
        ip="$hostip"
    fi
    echo 'Does the spec already exist on IAM? (y/n)'
    read answer
    if [ "$answer" == "y" ]; then
        curl -X PATCH http://$ip:8001/default/files/specs/FHIRSpec.json \
            -o "iam-patch.txt" \
            -F "contents=data/FHIRSpec.json"

    else
        curl -X POST http://$ip:8001/default/files \
            -o "iam-post.txt" \
            -F "path=specs/FHIRSpec.json" \
            -F "contents=data/FHIRSpec.json"
    fi
    echo 'Posted new spec to IAM.'
fi
echo 'Press Enter to finish run.'

read final
