#Dockerfile para nuestra base de datos PostgreSQL.

#defina el repositorio donde se descargará PostgreSQL usando la política FROM
# cuando ejecute el proceso de compilación del contenedor, también debería ejecutar el archivo create.sql
FROM postgres

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d