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
  Esquema del escenario: Comprar un producto como invitado termina con pago exitoso y factura
    Dado que el usuario está en la tienda
    Cuando busca "<producto>"
    Y abre "<producto>" desde los resultados
    Y agrega el producto al carrito
    Y abre el carrito
    Entonces ve en el carrito "<producto>" con cantidad 1 y el mismo precio del detalle
    Cuando continúa la compra como invitado con un comprador de prueba
    Y ingresa la dirección del comprador
    Y paga con una tarjeta de prueba
    Entonces ve que el pago fue exitoso
    Cuando confirma el pedido
    Entonces recibe un número de factura

    Ejemplos:
      | producto           |
      | Thor Hammer        |
      | Combination Pliers |
      | Cordless Drill 12V |
