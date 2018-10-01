# es el encargado de ensamblar la imagen de nuestro contenedor y compilar la aplicación.
FROM golang:latest 
#sirve para decirle cuál es el nombre de nuestra aplicación y versión:
LABEL Name=userservice Version=0.0.1 
#creando los directorios de espacio de trabajo predeterminados de Go
#uso de ENV 2 veces
#1. para crear la aplicación GOPATH (si no Go no puede pasar por el proceso de construcción)
#2. asociar GOPATH al PATH del sistema operativo de nuestro contenedor
RUN mkdir -p /go/src \
  && mkdir -p /go/bin \
  && mkdir -p /go/pkg
  ENV GOPATH=/go
  ENV PATH=$GOPATH/bin:$PATH
#crear el directorio de nuestra aplicación
  RUN mkdir -p $GOPATH/src/app
#indicar la ubicación del contenedor en nuestra aplicación dentro del sistema operativo del contenedor
#WORKDIR para decir que este es nuestro directorio de trabajo
  ADD . $GOPATH/src/app
  WORKDIR $GOPATH/src/app
#RUN para ejecutar la construcción de nuestro proceso de solicitud. 
#El binario generado tendrá el nombre principal y será ejecutado por la política CMD
  RUN go build -o main .
  CMD ["/go/src/app/main"]

  EXPOSE 3000