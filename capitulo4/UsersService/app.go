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

//METODO CRUD
//El primer método será el responsable de obtener un solo usuario; getUser.
func (a *App) getUser(w http.ResponseWriter, r *http.Request) { 
      vars := mux.Vars(r) 
      id, err := strconv.Atoi(vars["id"]) 
      if err != nil { 
       respondWithError(w, http.StatusBadRequest, "Invalid product ID") 
       return 
		 }

		 if value, err := a.Cache.getValue(id); err == nil && len(value) != 0 { 
			w.Header().Set("Content-Type", "application/json") 
			w.WriteHeader(http.StatusOK) 
			w.Write([]byte(value)) 
			return 
		}
   
		user := User{ID: id} 
		if err := user.get(a.DB); err != nil { 
		  switch err { 
			case sql.ErrNoRows: 
			   respondWithError(w, http.StatusNotFound, "User not found") 
			default: 
			   respondWithError(w, http.StatusInternalServerError, err.Error()) 
		  } 
		  return 
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