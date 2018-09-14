#Dockerfile para el contenedor CommandStack
#tiene variables de entorno y el archivo inicial responsable de la creación de las bases de datos

FROM postgres 
 
ENV POSTGRES_USER=postgres 
ENV POSTGRES_PASSWORD=postgres 
 
# run create.sql on init 
ADD create.sql /docker-entrypoint-initdb.d