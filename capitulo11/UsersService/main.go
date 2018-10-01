//Este es el archivo responsable de enviar los ajustes necesarios para el
// funcionamiento de nuestro microservicio a nuestra aplicación y para ejecutar el propio microservicio

//instanciamos una conexión a la base de datos desde el principio. Esta instancia es la base de datos que se utilizará en cada aplicación
package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

const (
	createUsersQueue = "CREATE_USER"
	updateUsersQueue = "UPDATE_USER"
	deleteUsersQueue = "DELETE_USER"
	portAddr         = ":50051" //añadido capitulo11
)

func main() {
	var numWorkers int
	cache := Cache{Enable: true}

	flag.StringVar(
		&cache.Address,
		"redis_address",
		os.Getenv("APP_RD_ADDRESS"),
		"Redis Address",
	)

	flag.StringVar(
		&cache.Auth,
		"redis_auth",
		os.Getenv("APP_RD_AUTH"),
		"Redis Auth",
	)

	flag.StringVar(
		&cache.DB,
		"redis_db_name",
		os.Getenv("APP_RD_DBNAME"),
		"Redis DB name",
	)

	flag.IntVar(
		&cache.MaxIdle,
		"redis_max_idle",
		10,
		"Redis Max Idle",
	)

	flag.IntVar(
		&cache.MaxActive,
		"redis_max_active",
		100,
		"Redis Max Active",
	)

	flag.IntVar(
		&cache.IdleTimeoutSecs,
		"redis_timeout",
		60,
		"Redis timeout in seconds",
	)
	flag.IntVar( 
		&numWorkers,  
		"num_workers",  
		10,  
		"Number of workers to consume queue" 
	 )

	flag.Parse()
	cache.Pool = cache.NewCachePool()

	connectionString := os.Getenv("DATABASE_DEV_URL")

	db, err := sqlx.Open("postgres", connectionString)
	if err != nil {
		log.Fatal(err)
	}

	go UsersToDB(numWorkers, db, cache, createUsersQueue) 
    go UsersToDB(numWorkers, db, cache, updateUsersQueue) 
    go UsersToDB(numWorkers, db, cache, deleteUsersQueue)

	a := App{}
	a.Initialize(cache, db)
	go a.runGRPCServer(portAddr) //añadido capitulo11, rutina para que los dos servidores funcionen al mismo tiempo: el servidor API y el servidor gRPC 
	a.Run(":3000")
}

//Nuestro método principal envía a la instancia App lo necesario para conectar la base de datos.
//Al final de todas las configuraciones, crearemos un nuevo grupo de conexiones con el método NewCachePool y pasaremos el puntero a nuestra instancia de caché

func (cache *Cache) enqueueValue(queue string, uuid int) error {
	if cache.Enable {
		conn := cache.Pool.Get()
		defer conn.Close()
		_, err := conn.Do("RPUSH", queue, uuid)
		return err
	}
	return nil
}
