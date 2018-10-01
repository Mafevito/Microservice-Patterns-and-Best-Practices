package main

import (
	"log"
	"time"

	redigo "github.com/garyburd/redigo/redis"
)

//Pool es la interfaz para el pool de Redis
type Pool interface {
	Get() redigo.Conn
}

type Cache struct {
	Enable bool

	MaxIdle int

	MaxActive int

	IdleTimeoutSecs int

	Address string

	Auth string

	DB string

	Pool *redigo.Pool
}

//método de nuestra estructura responsable de darnos un nuevo pool de conexiones
// NewCachePool return a new instance of the redis pool
func (cache *Cache) NewCachePool() *redigo.Pool {
	if cache.Enable {
		pool := &redigo.Pool{
			MaxIdle:     cache.MaxIdle,
			MaxActive:   cache.MaxActive,
			IdleTimeout: time.Second * time.Duration(cache.IdleTimeoutSecs),
			Dial: func() (redigo.Conn, error) {
				c, err := redigo.Dial("tcp", cache.Address)
				if err != nil {
					return nil, err
				}
				if _, err = c.Do("AUTH", cache.Auth); err != nil {
					c.Close()
					return nil, err
				}
				if _, err = c.Do("SELECT", cache.DB); err != nil {
					c.Close()
					return nil, err
				}
				return c, err
			},
			TestOnBorrow: func(c redigo.Conn, t time.Time) error {
				_, err := c.Do("PING")
				return err
			},
		}
		c := pool.Get() // Test connection during init
		if _, err := c.Do("PING"); err != nil {
			log.Fatal("Cannot connect to Redis: ", err)
		}
		return pool
	}
	return nil
}

//método que busca en nuestra caché y que introduce los datos en nuestra caché
func (cache *Cache) getValue(key interface{}) (string, error) {
	if cache.Enable {
		conn := cache.Pool.Get()
		defer conn.Close()
		value, err := redigo.String(conn.Do("GET", key))
		return value, err
	}
	return "", nil
}

func (cache *Cache) setValue(key interface{}, value interface{}) error {
	if cache.Enable {
		conn := cache.Pool.Get()
		defer conn.Close()
		_, err := redigo.String(conn.Do("SET", key, value))
		return err
	}
	return nil
}

//opciones que se pueden pasar a la línea de comandos
