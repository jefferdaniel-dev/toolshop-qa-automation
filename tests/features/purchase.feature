# language: es
Característica: Compra de productos

  @search
  Esquema del escenario: Buscar un producto muestra resultados que lo contienen
    Dado que el usuario está en la tienda
    Cuando busca "<producto>"
    Entonces ve resultados y todos contienen "<producto>"

    Ejemplos:
      | producto           |
      | Thor Hammer        |
      | Combination Pliers |
      | Cordless Drill 12V |

  @cart
  Esquema del escenario: Agregar un producto al carrito lo muestra con su precio
    Dado que el usuario está en la tienda
    Cuando busca "<producto>"
    Y abre "<producto>" desde los resultados
    Y agrega el producto al carrito
    Y abre el carrito
    Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle

    Ejemplos:
      | producto           |
      | Thor Hammer        |
      | Combination Pliers |
      | Cordless Drill 12V |

  @checkout
  Esquema del escenario: Comprar un producto según el tipo de acceso termina con pago exitoso y factura
    Dado que el usuario usa el acceso "<acceso>"
    Y que el usuario está en la tienda
    Cuando busca "<producto>"
    Y abre "<producto>" desde los resultados
    Y agrega el producto al carrito
    Y abre el carrito
    Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle
    Cuando continúa la compra
    Y ingresa la dirección "<calle>" "<numero>" con código postal "<codigo_postal>" en "<pais>"
    Entonces la ciudad y el estado se autocompletan según el código postal
    Cuando paga con una tarjeta de prueba
    Entonces ve que el pago fue exitoso
    Cuando confirma el pedido
    Entonces recibe un número de factura

    @invitado
    Ejemplos: Invitado
      | producto           | acceso         | pais | codigo_postal | numero | calle                |
      | Thor Hammer        | invitado       | CO   | 110321        | 15-88  | Carrera 6            |
      | Combination Pliers |                | NL   | 1071XX        | 1      | Museumstraat         |

    @login
    Ejemplos: Login
      | producto           | acceso         | pais | codigo_postal | numero | calle                |
      | Thor Hammer        | login_checkout | US   | 10118         | 350    | 5th Avenue           |
      | Combination Pliers | login_home     | US   | 94043         | 1600   | Amphitheatre Parkway |
      | Cordless Drill 12V | login_home     | DE   | 11011         | 1      | Platz der Republik   |
