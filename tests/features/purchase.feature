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

  @compra
  Esquema del escenario: Comprar un producto según el acceso y la etapa
    Dado que el usuario está en la tienda
    Y que el usuario usa el acceso "<acceso>"
    Y que la compra llega hasta la etapa "<etapa>"
    Cuando busca "<producto>"
    Y abre "<producto>" desde los resultados
    Y agrega el producto al carrito
    Y abre el carrito
    Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle
    Cuando continúa la compra
    Y ingresa la dirección "<calle>" "<numero>" con código postal "<codigo_postal>" en "<pais>"
    Entonces la ciudad y el estado se autocompletan según el código postal
    Cuando llena la tarjeta de prueba
    Entonces la compra termina según la etapa

    # acceso:
    #   invitado o vacío = compra sin cuenta, con un comprador sintético al azar
    #   login_home       = inicia sesión desde la home antes de buscar
    #   login_checkout   = inicia sesión en el paso de login del checkout
    # etapa:
    #   checkout     = llena todo y se detiene antes de pagar (el botón de pagar queda habilitado)
    #   confirmacion = paga y obtiene factura

    Ejemplos:
      | producto           | acceso         | etapa        | pais | codigo_postal | numero | calle                |
      | Thor Hammer        | login_checkout | confirmacion | US   | 10118         | 350    | 5th Avenue           |
      | Cordless Drill 12V | login_home     | checkout     | DE   | 11011         | 1      | Platz der Republik   |
      | Thor Hammer        | invitado       | checkout     | CO   | 110321        | 15-88  | Carrera 6            |
      | Combination Pliers |                | confirmacion | NL   | 1071XX        | 1      | Museumstraat         |
