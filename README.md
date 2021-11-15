# Prueba técnica para Z1
_Esta aplicación ha sido desarrollada como solución a la prueba técnica planteada por la empresa Z1. 
Espero que esta guía pueda ayudar a los revisores, para que su tarea no sea demasiado pesada_

## Herramientas utilizadas para el desarrollo
¿Qué se ha utilizado para el desarrollo de la API?
* **Python**
* **Django**
* **PostgreSQL**
* **GraphQL**

## Pre-requisitos
Antes de interactuar con la API se deben tener instalados en el sistema Python 3 (para el desarrollo se ha utilizado la versión 3.9.6),
PostgreSQL y por útltimo una serie de paquetes que serán necesarios. Para la instalación de estos paquetes se ha creado el archivo requirements.txt y se debe ejecutar en un terminal:
```
pip install -r requirements.txt 
```

Se debe tener creada una base de datos en postgres, en nuestro entorno local. 
Para poder incluirla en el proyecto debe crearse un archivo .env dentro de Z1Test/Z1Test (es decir, al mismo nivel que settings.py),
donde se incluirán los datos necesarios para la conexión con la base de datos. Un ejemplo sería la siguiente línea:
```
DATABASE_URL=postgres://usuario:password@127.0.0.1:5432/nombre_database
```
Donde se debe indicar el nombre de la base de datos junto con el usuario y la contraseña.
Con este .env conseguimos un nivel extra de seguridad, ya que este archivo no se compartirá en GitHub.
Además puede utilizarse en el futuro para guardar distintos parámetros sensibles (como SECRET_KEY) o datos en general que no queramos que sean filtrados.


Una vez realizados estos pasos, deben realizarse las migraciones necesarias para poner en funcionamiento la api, para ello se ejecutará en la raíz del proyecto:
```
python manage.py makemigrations
python manage.py migrate
```

## API
Siguiendo los pasos anteriores ya tendríamos instaladas todas las dependencias y conectada la base de datos al proyecto.
El siguiente paso sería lanzar la API para poder probarla, por lo que habría que ejecutar el siguiente comando:
```
python manage.py runserver
```
Con ello la API estaría lista para usar en la dirección _http://127.0.0.1:8000/_, donde encontraremos dos endpoints: 
_/admin/_ que viene por defecto en django y _/graphql/_, que se usará para realizar todas las peticiones.

### Estructura de la API
La estructura de la API es sencilla e intuitiva. En la raíz tendremos la carpeta principal del proyecto, la de la api y los archivos de manage.py y README.me.
En la carpeta principal estará alojado el archivo settings.py para las distintas configuraciones, el urls.py para nuestras rutas, asgi.py, wsgi.py y por último alojaremos aquí el archivo .env antes comentado.
En la carpeta de la api tendremos los archivos que vienen por defecto al crear una app junto con algunos nuevos, como types.py, schema.py y mutations.py que serán de utilidad para trabajar con GraphQL. 
Por último añadir que el archivo de tests.py se ha sustituido por un paquete donde dentro encontraremos tests de la aplicación separados por archivos junto con un utils.py con funciones comunes. 

### Modelos
Primero veremos cómo se han creado los modelos para llevar a cabo este proyecto. Se han creado 4 clases:
* **User**: hereda directamente de _AbstractUser_ y se ha dejado ya creada (aunque vacía) para posibles ampliaciones que se quieran hacer respecto a los usuarios.
* **Profile**: está ligado a cada usuario y se usará para administrar la lista de followers y followed (seguidores y personas a las que seguimos).
* **FollowRequest**: aquí se almacenarán todas las peticiones de seguimiento que se hagan (cuyo posibles estados son pending, accepted o rejected y por defecto pending).
* **Idea**: por último la tabla de ideas, relacionadas con el usuario que las creó y con un parámetro de visibilidad (cuyo posibles estados son public, protected o private).

### Queries de GraphQL
Ahora se pasará a describir brevemente los tipos de queries que se han desarrollado para obtener datos:
* **users**: devolverá un listado con todos los usuarios creados, pero sólo podrán usarlo los superusers. Esta query se ha creado para la posibilidad de que haya un superusuario supervisor que quiera obtener todos los datos.
```
{
  users{
    username
    email
  }
}
```
* **user**: con esta query se podrán buscar usuarios registrados, se debe especificar un nombre de usuario o parte de él y devolverá todos los usuarios con alguna coincidencia en el nombre.
```
{
  user(username: "user1"){
    username
    email
  }
}
```
* **requests**: cualquier usuario que utilice esta query obtendrá el listado de peticiones que tiene, puede especificar el estado de las mismas (status), por si quiere filtrar por todas las pendientes, aceptadas o rechazadas.
```
{
  requests(status: "pending"){
    fromUser{
        username
      }
    toUser{
      username
    }
    status
  }
}
```
* **ideas**: los usuarios podrán consultar todas sus ideas publicadas por orden de novedad pudiendo filtrar por la visibilidad de las mismas. Si se especifica un nombre de usuario, en lugar de devolver las ideas del usuario que realiza la petición devolverá las del especificado, pudiendo leer las públicas o las protegidas si eres seguidor del mismo.
```
{
  ideas{
    user{
      username
    }
    visibility
    text
  }
}
```
* **allIdeas**: con esta query, un usuario obtendrá todas sus ideas y además las públicas del resto de usuarios y protegidas de los que sigue, todo en orden de novedad.
```
{
  allIdeas{
    user{
      username
    }
    visibility
    text
  }
}
```
* **followersByUser**: cada usuario podrá consultar la lista de seguidores que tiene.
```
{
  followersByUser(username:"user2"){
    username
    email
    password
  }
}

```
* **followedByUser**: cada usuario podrá consultar la lista de gente a la que sigue.
```
{
  followedByUser(username:"user3"){
    username
    email
    password
  }
}
```

### Mutaciones de GraphQL
En este apartado se comentará los distintos grupos de mutaciones que se han desarrollado para la API:
* **tokenAuth**: esta mutación la ofrece directamente el paquete graphql_jwt y se usará para el login. Necesitará como parámetro de entrada el nombre de usuario y la password y se obtendrá el token (entre otros parámetros relacionados) con el que poder hacer el resto de peticiones. Junto a esta mutación está _verifyToken_ y _refreshToken_ ofrecidas por el mismo paquete.
```
mutation{
    tokenAuth(username:"user1", password:"password1"){
        token
    }
}
```
* **createUser**: para crear usuarios no será necesario estar logado en el sistema, se debe introducir un nombre de usuario libre, un email y una password.
```
mutation{
  createUser(userData: {username:"test", email:"test@gmail.com", password:"test"}){
    user{
      username
      email,
      password
    }
  }
}
```
* **updateUser**: para editar los parámetros de un usuario, como la password.
```
mutation{
  updateUser(userData: {password: "new_password"}){
    user{
      username
      email,
    }
  }
}
```
* **deleteUser**: para eliminar un usuario.
```
mutation{
  deleteUser{
    user{
      username
      email
    }
  }
}
```
* **createFollowRequest**: para crear una petición de seguimiento. Se necesitará el nombre de usuario al que se quiere seguir y se creará por defecto en estado 'pending'.
```
mutation{
  createFollowRequest(followRequestData: {toUser:"user2"}){
    followRequest{
      fromUser{
        username
      }
      toUser{
        username
      }
      status
    }
  }
}
```
* **updateFollowRequest**: para modificar una petición, y poder así aceptarla o rechazarla.
```
mutation{
  updateFollowRequest(followRequestData: {fromUser: "user1", status:"accepted"}){
    followRequest{
      fromUser{
        username
      }
      toUser{
        username
      }
      status
    }
  }
}
```
* **createIdea**: con esta mutuación, los usuarios podrán crear ideas. Deberán introducir el texto y la visibilidad correspondiente.
```
mutation{
  createIdea(ideaData: {text:"user1 text", visibility:"public"}){
    idea{
      text
      visibility
      user{
        username
      }
    }
  }
}
```
* **updateIdea**: para modificar una idea, se podrá cambiar tanto el texto como la visibilidad.
```
mutation{
  updateIdea(ideaData: {id: 1, visibility:"public"}){
    idea{
      text
      visibility
      user{
        username
      }
    }
  }
}
```
* **deleteIdea**: para que los usuarios puedan elimninar una idea especificando el ID correspondiente a la misma.
```
mutation{
  deleteIdea(ideaData: {id: 1}){
    idea{
      text
      visibility
      user{
        username
      }
    }
  }
}
```
* **deleteFollower**: para que los usuarios puedan eliminar un seguidor que se especificará con el nombre de usuario.
```
mutation{
  deleteFollower(follower:"user3"){
    followers{
      username
    }
  }
}
```
* **deleteFollowed**: para que los usuarios puedan dejar de seguir a alguien que especificarán con el nombre de usuario.
```
mutation{
  deleteFollowed(followed:"user3"){
    all_followed{
      username
    }
  }
}
```

### Detalles y mejoras de la API
En los apartados anteriores se han comentado todas las consultas, ya sea en forma de query o mutation, que se pueden hacer a la API.
Destacar que para realizar dichas consultas, el usuario que realice la petición debe estar logado y por ello añadir el correspondiente token a la consulta (con excepción de las consultas para token y de crear usuario, que no se necesita estar logado para realizarlas).

Se han desarrollado distintos tests que prueben la API al completo y así añadan robustez a la misma. Se encuentran dentro del directorio api, en la carpeta de test.
Dentro se encontraran separados por archivos los tests para usuario (crear, actualizar, eliminar y logarse junto con algús test de comprobación de errores), 
idea (crear, actualizar, eliminar, obtener las ideas de un usuario, obtener las ideas de otro usuario y por último ver todas las ideas posibles, tanto del propio usuario como del resto según la visibilidad)
y peticiones de seguimiento (crear, aceptar o rechazar una petición junto con eliminar a un seguidor o dejar de seguir a un usuario).
Para lanzar la batería de test basta con ejecutar desde la raíz del proyecto:
```
python manage.py test
```


Se procederá a comentar y proponer ciertas mejoras de la API desarrollada:
* **Cambio de contraseña con magic link**: para este apartado que no dió tiempo a realizarse, quizás podría investigarse alguna de las mutaciones que ya ofrece el paquete graphql_auth, como sendPasswordResetEmail y por supuesto definir en settings toda la gestión de emails.
* **Notifaciones push**: desarrollar notificaciones push, no sólo para cuando un usuario que seguimos publique una idea, también para cuando se recibe una petición y otros casos interesantes.
* **Settings**: aunque ya se ha comentado que para este proyecto es necesario un archivo .env para especificar la base de datos, podría también usarse para almacenar ciertos parámetros sensibles (como SECRET_KEY) o distintas configuraciones que quieran darse.
* **Gestión de errores**: otro punto muy importante a mejorar, se debería hacer un profundo análisis de los distintos errores que podrían darse y distintas formas de gestionarlos y hacérselos llegar al usuario.
* **Superuser**: sólo se ha desarrollado un endpoint para ver todos los usuarios en caso de que seas superusuario, pero podrían desarrollarse más en caso de que se tuviera pensado establecer este tipo de rol en cierto usuario con privilegios.
* **Modelo de usuario**: como se ha comentado antes, el modelo de usuario que hereda de AbstractUser, se ha dejado creado en los modelos pero sin ningún tipo de ampliación por si en el futuro se pretende ampliar o añadir algún campo.
* **Mejoras a nivel de aplicación**: debido a que la prueba técnica era crear una pequeña red social, se podrían añadir ciertas mejoras, como creación de ideas 'fugaces' que estén visibles durante solo un día, poder clasificar a tus seguidores para que puedan acceder a contenidos que otros no pueden, etc...

## Agradecimientos
Quería aprovechar este pequeño apartado para expresar mi gratitud a la empresa Z1 por confiar en mi trabajo y permitirme realizar esta prueba.
Siempre es un reto enfrentarte a desarrollos con nuevas tecnologías o herramientas nuevas, y en este caso ha sido mi primera vez con Graphql.
He disfrutado mucho aprendiendo e intentando adaptarme para poder ofrecer la mejor solución posible (o al menos la mejor que en ese momento se me ha ocurrido).
También el desarrollo en django, ya que en los último proyectos he realizado siempre desarrollos con flask, pero volver a django siempre es un placer!
He intentado llevar a cabo ciertas buenas prácticas siguiendo siempre PEP8 (un referente en el mundo de Python). 
Espero que revisar esta prueba no sea una tarea dura y ante cualquier duda, podéis contactar conmigo para resolverla.
