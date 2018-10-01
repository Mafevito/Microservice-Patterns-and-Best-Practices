//Este archivo es responsable de recibir los datos y enviarlos a nuestro almacenamiento de datos
//El signo de subrayado antes de la importación significa que estamos invocando el método init dentro de esta librería
package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"net/http"
	"strconv"

	"github.com/codegangsta/negroni"
	"github.com/gorilla/mux"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	pb "github.com/viniciusfeitosa/BookProject/UsersService/user_data"
  "google.golang.org/grpc"
  "google.golang.org/grpc/reflection"
)
//es la estructura con los valores de configuración de la aplicación
type App struct { 
	DB                   *sqlx.DB 
	Router           *mux.Router 
	Cache            Cache
  }
//Inicializa la creación de la conexión a la base de datos y prepara todas las rutas
func (a *App) Initialize(cache Cache, db *sqlx.DB) { 
  a.Cache = cache
	a.DB = db 
	a.Router = mux.NewRouter() 
	a.initializeRoutes() 
}
//ahora es el momento de definir las rutas en el método initializeRoutes
func (a *App) initializeRoutes() { 
	a.Router.HandleFunc("/users", a.getUsers).Methods("GET") 
	a.Router.HandleFunc("/user", a.createUser).Methods("POST") 
	a.Router.HandleFunc("/user/{id:[0-9]+}",  
	 a.getUser).Methods("GET") 
	a.Router.HandleFunc("/user/{id:[0-9]+}",    
	 a.updateUser).Methods("PUT") 
	a.Router.HandleFunc("/user/{id:[0-9]+}", 
	 a.deleteUser).Methods("DELETE") 
	 a.Router.HandleFunc("/healthcheck", a.healthcheck).Methods("GET")
	 a.Router.HandleFunc("/sentryerr", a.sentryerr).Methods("GET")
  }
//Run inicializa el servidor, inicializa el microservicio
func (a *App) Run(addr string) { 
	n := negroni.Classic() 
	n.UseHandler(a.Router) 
	log.Fatal(http.ListenAndServe(addr, n)) 
 }
// Dos funciones de ayuda 
//La primera función es responsable de pasar a la capa HTTP, los códigos de error que se pueden generar dentro de la aplicación
//La segunda función es la encargada de crear los JSONs que deben ser respondidos para cada solicitud
 func respondWithError(w http.ResponseWriter, code int, message 
	string) { 
	 respondWithJSON(w, code, map[string]string{"error": message}) 
   } 
   func respondWithJSON(w http.ResponseWriter, code int, payload     
	interface{}) { 
	 response, _ := json.Marshal(payload) 

	 w.Header().Set("Content-Type", "application/json") 
	 w.WriteHeader(code) 
	 w.Write(response) 
	 }

	/* añadido cap13, registro de errores*/
	/* manejador que genera los errores para Sentry */
	func (a *App) sentryerr(w http.ResponseWriter, r *http.Request) {
			//La siguiente línea creará un error porque el archivo que intentamos leer no existe
			_, err := os.Open("filename.ext")
			// capturamos el error y lo enviamos a Sentry, mientras devolvemos un error en la respuesta HTTP
			if err != nil {
				raven.CaptureErrorAndWait(err, nil)
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
			//Si no se produce ningún error, la respuesta será positiva
			w.Write([]byte("OK"))
       return
}


	/* Añadido cap13, supervisión de un servicio unico */
	/* Nagios core es una herramienta para el monitoreo de multiples servicios*/
	//crearemos el handler para esta nueva ruta. Comenzamos con el nombre del método, junto con sus parámetros
	func (a *App) healthcheck(w http.ResponseWriter, r *http.Request) {
   		//escribiremos una variable para recopilar los errores, buscar una conexión de Pool desde la caché y preparar el retorno de la conexión al Pool
			 var err error
       c := a.Cache.Pool.Get()
			 defer c.Close()
			 
			//Hagamos la primera validación, que es comprobar si la caché está activa
      // Check Cache
			_, err = c.Do("PING")

			//hacemos una segunda validación, que consiste en comprobar si la base de datos está activa
			// Check DB
			err = a.DB.Ping()

			//Si uno de los componentes no está disponible, devolveremos un error a la herramienta de monitorización
			if err != nil {
				http.Error(w, "CRITICAL", http.StatusInternalServerError)
				return
			}
			
			//Si no hay ningún error en los componentes de la aplicación, se devuelve un mensaje indicando que todo está normal
			w.Write([]byte("OK"))
			return
}


		//METODO CRUD
//El primer método será el responsable de obtener un solo usuario; getUser.
func (a *App) getUser(w http.ResponseWriter, r *http.Request) { 
      vars := mux.Vars(r) 
      id, err := strconv.Atoi(vars["id"]) 
      if err != nil { 
       respondWithError(w, http.StatusBadRequest, "Invalid product ID") 
       return 
		 }
    //busca directamente desde la caché
		func (a *App) getUserFromCache(id int) (string, error) {
			if value, err := a.Cache.getValue(id); err == nil && 
						len(value) != 0 {
				 return value, err
			}
			return "", errors.New("Not Found")
	 }
   // busca en la base de datos si no se encuentra ningún dato en la caché
	 func (a *App) getUserFromDB(id int) (User, error) {
		user := User{ID: id}
		if err := user.get(a.DB); err != nil {
			switch err {
				 case sql.ErrNoRows:
						 return user, err
						default:
							return user, err
			}
		}
		return user, nil
 }

 //estructura que servirá como manejador lógico para proporcionar los datos del usuario
 type userDataHandler struct {
	app *App
 }
//código responsable de componer el tipo de respuesta que espera el gRPC
 func (handler *userDataHandler) composeUser(user User) 
       *pb.UserDataResponse {
      return &pb.UserDataResponse{
        Id:    int32(user.ID),
				Email: user.Email,
				Name:  user.Name,
      }
		}
//método responsable de recibir la solicitud a través del gRPC
func (handler *userDataHandler) GetUser(ctx context.Context,
	request *pb.UserDataRequest) (*pb.UserDataResponse, error) {
var user User
var err error
if value, err := handler.app.getUserFromCache(int(request.Id)); 
		 err == nil {
	if err = json.Unmarshal([]byte(value), &user); err != nil {
		 return nil, err
	}
	return handler.composeUser(user), nil
}
if user, err = handler.app.getUserFromDB(int(request.Id)); 
		err == nil {
 return handler.composeUser(user), nil
}
return nil, err
}

//Con la petición y la respuesta preparadas, escribamos el código del servidor gRPC.
//Primero, declaramos el nombre del método que ejecutará el servidor:
func (a *App) runGRPCServer(portAddr string) {
 //Luego, preparamos al oyente del servidor
	lis, err := net.Listen("tcp", portAddr)
    if err != nil {
      log.Fatalf("failed to listen: %v", err)
		}
	//Creamos la instancia del servidor y la registramos en el gRPC. Si no tenemos ningún tipo de error, tendremos nuestra capa de comunicación utilizando el gRPC funcionando perfectamente
	s := grpc.NewServer()
    pb.RegisterGetUserDataServer(s, &userDataHandler{app: a})
    reflection.Register(s)
    if err := s.Serve(lis); err != nil {
      log.Fatalf("failed to serve: %v", err)
    }
   }




   
		/*respondWithJSON(w, http.StatusOK, user) 
		}*/
		response, _ := json.Marshal(user) 
     if err := a.Cache.setValue(user.ID, response); err != nil { 
       respondWithError(w, http.StatusInternalServerError, err.Error()) 
       return 
     } 
 
     w.Header().Set("Content-Type", "application/json") 
     w.WriteHeader(http.StatusOK) 
     w.Write(response) 
		}
		
//El segundo método sera el responsable de obtener muchos usuarios a la vez; getUsers.
	func (a *App) getUsers(w http.ResponseWriter, r *http.Request) { 
		count, _ := strconv.Atoi(r.FormValue("count")) 
		start, _ := strconv.Atoi(r.FormValue("start")) 
   
		if count > 10 || count < 1 { 
		  count = 10 
		} 
		if start < 0 { 
		  start = 0 
		} 
   
		users, err := list(a.DB, start, count) 
		if err != nil { 
		  respondWithError(w, http.StatusInternalServerError, err.Error()) 
		  return 
		} 
   
		respondWithJSON(w, http.StatusOK, users) 
	  }
//Ahora, pasamos a los métodos que generan cambios en la base de datos
//Método createUser
func (a *App) createUser(w http.ResponseWriter, r *http.Request) { 
	var user User 
	decoder := json.NewDecoder(r.Body) 
	if err := decoder.Decode(&user); err != nil { 
	  respondWithError(w, http.StatusBadRequest, "Invalid request payload") 
	  return 
	}
	defer r.Body.Close() 
	    // get sequence from Postgres 
			a.DB.Get(&user.ID, "SELECT nextval('users_id_seq')")

			JSONByte, _ := json.Marshal(user) 
     if err := a.Cache.setValue(user.ID, string(JSONByte)); err != nil { 
                 respondWithError(w, http.StatusInternalServerError, err.Error()) 
                 return 
     } 
 
     if err := a.Cache.enqueueValue(createUsersQueue, user.ID); err != nil { 
                 respondWithError(w, http.StatusInternalServerError, err.Error()) 
                 return 
     } 
 
		 respondWithJSON(w, http.StatusCreated, user)
		

      if err := user.create(a.DB); err != nil { 
        fmt.Println(err.Error()) 
        respondWithError(w, http.StatusInternalServerError, err.Error()) 
        return 
      } 
 
      respondWithJSON(w, http.StatusCreated, user) 
    }
//Método updateUser
func (a *App) updateUser(w http.ResponseWriter, r *http.Request) { 
	vars := mux.Vars(r) 
	id, err := strconv.Atoi(vars["id"]) 
	if err != nil { 
	  respondWithError(w, http.StatusBadRequest, "Invalid product ID") 
	  return 
	} 

	var user User 
	decoder := json.NewDecoder(r.Body) 
	if err := decoder.Decode(&user); err != nil { 
	  respondWithError(w, http.StatusBadRequest, "Invalid resquest payload") 
	  return 
	} 
	defer r.Body.Close() 
	user.ID = id
	if err := user.update(a.DB); err != nil { 
        respondWithError(w, http.StatusInternalServerError, err.Error()) 
        return 
      } 
 
      respondWithJSON(w, http.StatusOK, user) 
	}
//Método deleteUser
func (a *App) deleteUser(w http.ResponseWriter, r *http.Request) { 
	vars := mux.Vars(r) 
	id, err := strconv.Atoi(vars["id"]) 
	if err != nil { 
	  respondWithError(w, http.StatusBadRequest, "Invalid User ID") 
	  return 
	} 

	user := User{ID: id} 
	if err := user.delete(a.DB); err != nil { 
	  respondWithError(w, http.StatusInternalServerError, err.Error()) 
	  return 
	} 

	respondWithJSON(w, http.StatusOK, map[string]string{"result": "success"}) 
  }