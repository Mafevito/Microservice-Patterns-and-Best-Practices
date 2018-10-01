//declaramos el paquete en el que estamos trabajando,
//y luego las importaciones necesarias para el proyecto
package main
    import ( 
      "github.com/jmoiron/sqlx" 
      "golang.org/x/crypto/bcrypt" 
	)
//declaración de nuestra entidad, Usuarios
//el usuario es la estructura responsable de representar la entidad de la base de datos
	type User struct { 
        ID       int    `json:"id" db:"id"` 
        Name     string `json:"name" db:"name"` 
        Email    string `json:"email" db:"email"` 
        Password string `json:"password" db:"password"` 
	  }
	//para obtener una devolución, sólo tiene que actualizar la instancia de usuario con los datos de db
	//el acceso a la base de datos en PostgreSQL es a través de la inyección de dependencias, pasada como parámetro en el método get
	func (u *User) get(db *sqlx.DB) error { 
        return db.Get(u, "SELECT name, email FROM users WHERE id=$1",
         u.ID) 
	}
	//actualiza los datos en la base de datos utilizando los valores de instancia
	func (u *User) update(db *sqlx.DB) error { 
        hashedPassword, err := bcrypt.GenerateFromPassword( 
             []byte(u.Password), 
             bcrypt.DefaultCost, 
        ) 
        if err != nil { 
          return err 
        } 
        _, err = db.Exec("UPDATE users SET name=$1, email=$2,
         password=$3 WHERE id=$4", u.Name, u.Email,
         string(hashedPassword), u.ID) 
        return err 
	  }
	//Elimina la fecha de la base de datos utilizando los valores de instancia
	func (u *User) delete(db *sqlx.DB) error { 
        _, err := db.Exec("DELETE FROM users WHERE id=$1", u.ID) 
        return err 
	  }
	//Crea un nuevo usuario en la base de datos utilizando los valores de instancia
	func (u *User) create(db *sqlx.DB) error { 
        hashedPassword, err := bcrypt.GenerateFromPassword( 
          []byte(u.Password), 
          bcrypt.DefaultCost, 
        ) 
        if err != nil { 
		  return err
		} 
        return db.QueryRow( 
          "INSERT INTO users(name, email, password) VALUES($1, $2, $3)
           RETURNING id", u.Name, u.Email,
           string(hashedPassword)).Scan(&u.ID) 
	  }
	//List devuelve una lista de usuarios. Esto podría aplicarse a la paginación:
	func list(db *sqlx.DB, start, count int) ([]User, error) { 
        users := []User{} 
        err := db.Select(&users, "SELECT id, name,
         email FROM users LIMIT $1 OFFSET $2", count, start) 
        if err != nil { 
          return nil, err 
        } 
        return users, nil 
	  }
	//la lista no es un método, sino una función.la función de lista simplemente devuelve una lista de usuarios que reciben parámetros para posibles paginaciones de información.
   