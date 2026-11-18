# ACTIVIDAD DE AUTOAPRENDIZAJE

## SEGURIDAD DEL SISTEMA WEB DATALAN

### 1. Introducción

La seguridad de aplicaciones web consiste en proteger la confidencialidad, integridad y disponibilidad de la información que procesa una aplicación, así como la correcta identificación y autorización de quienes interactúan con ella. En un sistema de gestión operativa, la protección de credenciales, sesiones, permisos y datos de usuarios no es un complemento opcional: es una condición necesaria para que la plataforma cumpla su propósito sin comprometer la operación ni la trazabilidad de las actividades.

DATALAN gestiona solicitudes operativas, incidencias técnicas, perfiles de técnicos, decisiones comerciales, cronogramas y registros de actividad vinculados a servicios de fibra óptica. Ese tipo de información incluye usuarios, roles, responsables, relaciones entre servicios y registros funcionales. Por ello, la seguridad del sistema se concentra en varios puntos: autenticación, control de acceso por roles, manejo de sesiones, validación de entradas y protección de la capa web.

En este documento se analizan principalmente dos grandes dimensiones: (1) seguridad en el inicio de sesión, sesiones y manejo de contraseñas; y (2) seguridad en el diseño y desarrollo del sistema web DATALAN. El análisis se apoya en evidencias verificables del código fuente, especialmente en [settings.py](../DATALAN/DATALAN/settings.py), [auth_service.py](../DATALAN/DATALAN/auth_service.py), [views.py](../DATALAN/DATALAN/views.py), [urls.py](../DATALAN/DATALAN/urls.py), [login.html](../DATALAN/DATALAN/templates/login.html) y la batería de pruebas de iteración 1 [test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py).

### 2. Seguridad enfocada en el inicio de sesión y manejo de contraseñas

#### 2.0. Matriz general de mecanismos de seguridad identificados

| Mecanismo | Estado | Evidencia | Observación |
|---|---|---|---|
| Autenticación por sesión Django | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py), [auth_service.py](../DATALAN/DATALAN/auth_service.py), [views.py](../DATALAN/DATALAN/views.py) | El proyecto no usa `AbstractUser` ni `AuthenticationMiddleware` de forma clásica; usa una autenticación manual sobre la base de datos y la sesión de Django. |
| Cookies de sesión | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py) | Se usa `SESSION_ENGINE = 'django.contrib.sessions.backends.db'` y varias cookies de sesión con atributos de seguridad. |
| CSRF | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py), [login.html](../DATALAN/DATALAN/templates/login.html) | El middleware `CsrfViewMiddleware` está activo y las vistas formadas incorporan `{% csrf_token %}`. |
| Hash de contraseñas | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py), [auth_service.py](../DATALAN/DATALAN/auth_service.py) | Se usa `make_password()` y `check_password()`, con Argon2 y PBKDF2 como mecanismos disponibles. |
| Validación de complejidad | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py) | Se aplican validadores de longitud mínima, contraseñas comunes y numéricas. |
| Control de acceso por roles | IMPLEMENTADO Y VERIFICADO | [auth_service.py](../DATALAN/DATALAN/auth_service.py), [views.py](../DATALAN/DATALAN/views.py) | Se define una matriz de roles y se valida `request.session['role']` antes de entrar a pantallas. |
| Sesiones con expiración | IMPLEMENTADO Y VERIFICADO | [settings.py](../DATALAN/DATALAN/settings.py), [views.py](../DATALAN/DATALAN/views.py) | `SESSION_COOKIE_AGE = 1800`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`, `set_expiry(1800)` en login. |
| Protección HTTPS / cookies seguras | IMPLEMENTADO PARCIALMENTE | [settings.py](../DATALAN/DATALAN/settings.py) | Se habilitan medidas de seguridad HTTPS, pero los valores se controlan con variables de entorno y por defecto pueden permanecer en `False` en desarrollo. |
| Protección contra XSS | IMPLEMENTADO PARCIALMENTE | [settings.py](../DATALAN/DATALAN/settings.py), templates HTML | Django usa autoescape y las configuraciones de seguridad son parcialmente reforzadas; no se observa un sistema de sanitización especial customizado. |
| 2FA / JWT / tokens | NO IMPLEMENTADO | No se encontró evidencia del repositorio | No hay uso de `SimpleJWT`, `rest_framework.authtoken`, OTP ni dos factores. |
| Recuperación de contraseña | NO IMPLEMENTADO | No se encontró evidencia del repositorio | No existe flujo de restablecimiento seguro mediante correo, token o pregunta de seguridad. |
| Protección contra ataques de fuerza bruta | NO IMPLEMENTADO | No se encontró evidencia del repositorio | No hay bloqueo automático por intentos fallidos ni tasa de intentos. |

#### 2.1. Mecanismo de autenticación del sistema

La autenticación de DATALAN no se apoya en un modelo de usuario estándar de Django (`AbstractUser` o `AbstractBaseUser`). En su lugar, el proyecto define un servicio de autenticación propio en [auth_service.py](../DATALAN/DATALAN/auth_service.py), y la entrada principal del flujo ocurre en [views.py](../DATALAN/DATALAN/views.py).

La función relevante es la siguiente:

```python
@never_cache
def login_view(request):
    if current_user(request):
        return redirect(ROLES[request.session['role']]['home'])
    if request.method == 'POST':
        identity = authenticate(
            request.POST.get('username', ''),
            request.POST.get('password', ''),
        )
        if identity:
            request.session.cycle_key()
            request.session.set_expiry(1800)
            request.session['identity'] = identity
            request.session['role'] = identity['role']
            return redirect(ROLES[identity['role']]['home'])
        return render(request, 'login.html', {'error': 'Usuario, contraseña incorrectos o cuenta inactiva.'})
    return render(request, 'login.html')
```

La función `authenticate()` consulta el registro de usuarios de la base de datos de DATALAN. La consulta valida dos condiciones principales: (1) que el usuario esté activo; y (2) que el nombre de usuario o correo coincida con la entrada del usuario; posteriormente compara la contraseña usando la función `check_password()` de Django:

```python
SELECT u.user_id, u.username, u.full_name, u.identity_number,
       u.password_hash, r.role_key
FROM datalan.usuarios u
JOIN datalan.usuarios_roles ur ON ur.user_id = u.user_id
JOIN datalan.roles r ON r.role_id = ur.role_id
WHERE u.is_active
  AND (lower(u.username) = lower(%s) OR lower(u.email) = lower(%s))
ORDER BY ur.assigned_at
LIMIT 1
FOR UPDATE OF u
```

```python
password_valid = check_password(password, stored_password)
if not password_valid:
    return None
```

Este patrón indica que la autenticación del sistema depende de:

- credenciales de usuario (nombre de usuario o correo) y contraseña;
- verificación de si la cuenta está activa;
- consulta de rol asociado a la cuenta;
- validación de la contraseña mediante mecanismo seguro de Django;
- activación de sesión con información de identidad y rol.

La lógica de roles se define en `ROLES` y en la función `role_for(request)`, donde el rol se guarda en la sesión del navegador (`request.session['role']`). El acceso posterior se restringe por decoradores y controles de navegación, tal como se analiza más adelante.

#### 2.2. Gestión de sesiones

DATALAN configura sesiones de Django con almacenamiento en base de datos (`SESSION_ENGINE = 'django.contrib.sessions.backends.db'`), lo que implica que la información de la sesión se persiste en PostgreSQL y no solo en memoria. La configuración efectiva se observa en [settings.py](../DATALAN/DATALAN/settings.py):

```python
SESSION_COOKIE_SECURE = os.environ.get('DATALAN_SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_SECURE = os.environ.get('DATALAN_CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = True
```

El sistema además usa la función `request.session.cycle_key()` cuando el usuario inicia sesión. Esto es una medida relevante para mitigar el riesgo de fijación de sesión, porque crea una nueva clave de sesión después de autenticar al usuario. En la misma operación se establece el tiempo de expiración de la sesión a 1800 segundos (30 minutos):

```python
request.session.cycle_key()
request.session.set_expiry(1800)
request.session['identity'] = identity
request.session['role'] = identity['role']
```

Esto significa que la sesión se mantiene activa durante un período definido y se invalida al cerrar el navegador (`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`). Cuando el usuario cierra la sesión, se ejecuta `logout_view()`:

```python
@never_cache
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')
```

La función `flush()` elimina la sesión actual y destruye su contenido asociado. En el caso de que la sesión expire, la comprobación solicitada por los decoradores `@protected` exige que existan datos de identidad en la sesión; de lo contrario, redirige a `/login/?next=...`.

La cookie de sesión ofrece protección básica de confidencialidad por `HttpOnly`, y la cookie CSRF también tiene `HttpOnly` y `Secure` configurables por variable de entorno.

#### 2.3. Tokens y autenticación de doble factor

No se encontraron indicadores en el repositorio de que DATALAN utilice JWT, tokens de API, códigos temporales, verificación por correo o autenticación de dos factores (2FA). En la configuración de Django no aparece `rest_framework`, `rest_framework.authtoken`, `django-rest-framework-simplejwt`, ni una extensión de autenticación de dos pasos. Tampoco se observa un flujo de recuperación por correo, códigos OTP o validación por SMS.

En consecuencia, el estado real del proyecto es:

- JWT: NO IMPLEMENTADO.
- Tokens de sesión de Django: IMPLEMENTADO Y VERIFICADO para navegación web.
- 2FA: NO IMPLEMENTADO.
- Códigos temporales: NO IMPLEMENTADO.
- Verificación por correo para inicio de sesión: NO IMPLEMENTADO.

Esta conclusión debe interpretarse como evidencia del repositorio revisado, no como una afirmación sobre proyectos no incluidos en la revisión.

#### 2.4. Proceso completo del inicio de sesión

El flujo real del inicio de sesión puede describirse de la siguiente forma:

1. El usuario accede a [login.html](../DATALAN/DATALAN/templates/login.html), donde se presenta un formulario con `method="post"` y `{% csrf_token %}`.
2. El usuario introduce `username` y `password`.
3. La vista `login_view()` recibe la solicitud y llama a `authenticate(username, password)`.
4. La autenticación consulta la tabla de usuarios y los roles asociados, valida `u.is_active` y usa `check_password(password, stored_password)`.
5. Si las credenciales son correctas, se ejecuta `request.session.cycle_key()`, se fija la expiración y se guardan los datos de `identity` y `role`.
6. Django redirige al usuario a la ruta correspondiente según `ROLES[identity['role']]['home']`.
7. El acceso a pantallas protegidas se controla con decoradores `@protected` y `@admin_only`.
8. Si el usuario no está autenticado, se redirige a `/login/?next=...`; si la contraseña es incorrecta, se renderiza el mismo formulario con un error.
9. En el cierre de sesión, `logout_view()` hace `request.session.flush()` y devuelve al login.

```mermaid
flowchart TD
    A[Usuario entra a /login/] --> B{Formulario enviado?}
    B -- No --> C[Render login.html]
    B -- Sí --> D[login_view() recibe POST]
    D --> E[authenticate(username, password)]
    E --> F{Credenciales válidas y cuenta activa?}
    F -- No --> G[Render login.html con error]
    F -- Sí --> H[request.session.cycle_key()]
    H --> I[set_expiry(1800)]
    I --> J[Guardar identity y role]
    J --> K[Redirect a home del rol]
    K --> L{Acceso permitido?}
    L -- Sí --> M[Vista protegida]
    L -- No --> N[Redirect a acceso denegado]
    M --> O[logout_view() con session.flush()]
```

Es importante aclarar que la autenticación es personalizada; si un usuario no tiene sesión válida, la lógica no le permite avanzar a funcionalidades protegidas. La aplicación no muestra un formulario de restablecimiento de contraseña ni una confirmación vía correo, por lo que la seguridad de la autenticación se apoya principalmente en la calidad del hash, la gestión de la sesión y la autorización por roles.

#### 2.5. Almacenamiento de contraseñas en PostgreSQL

El almacenamiento de contraseñas se implementa en un esquema específico de PostgreSQL y no en un modelo estándar de Django. El archivo [auth_service.py](../DATALAN/DATALAN/auth_service.py) indica que la tabla principal es `datalan.usuarios`, con los campos `username`, `email`, `password_hash`, `is_active`, `last_login_at` y `identity_number`.

El esquema incluye la relación con `datalan.usuarios_roles` y `datalan.roles`, y la intención es mantener la asociación entre usuarios y permisos por rol.

La creación de usuarios se hace con `make_password()`:

```python
cursor.execute("""
    INSERT INTO datalan.usuarios
        (username, full_name, email, identity_number, password_hash)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING user_id
""", [
    user_data['username'],
    user_data['full_name'],
    user_data['email'],
    user_data.get('identity_number', ''),
    make_password(user_data['password']),
])
```

La validación se realiza con `check_password()`:

```python
password_valid = check_password(password, stored_password)
```

Esto implica que la contraseña nunca se compara como texto plano en la base de datos. En modo de ejecución real, lo que se persiste es un hash y la verificación se realiza comparando la contraseña introducida con ese valor usando la sal y el algoritmo asociado al hash.

No se observa un mecanismo de recuperación segura de contraseñas. No hay flujo de “reset password”, ni validación por email, ni generación de token temporal para restaurar la clave. Por tanto, el sistema protege la autenticación mediante hashing y validación de sesión, pero no incorpora recuperación segura ni rotación gestionada de credenciales.

#### 2.6. Algoritmo utilizado para proteger contraseñas

La configuración de [settings.py](../DATALAN/DATALAN/settings.py) define:

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

Además, el sistema usa `make_password()` y `check_password()`, que son funciones centrales de Django para generar y verificar hashes seguros. Esto significa que el proyecto admite, por configuración, algoritmos modernos y robustos, con prioridad a Argon2, y mantiene PBKDF2 como alternativa compatible. El orden del arreglo define el algoritmo preferido para nuevas contraseñas:

- Argon2: es un algoritmo moderno de hash configurado como prioridad.
- PBKDF2: mecanismo robusto y ampliamente aceptado, mantenido como respaldo y verificación de hashes históricos.

El uso de estos algoritmos es adecuado para DATALAN porque:

- evita el almacenamiento de contraseñas en texto plano;
- incorpora sal por cada contraseña para evitar ataques por tablas arco iris y precomputación;
- permite verificar las contraseñas de forma segura sin exponer la clave original;
- cumple con estándares de seguridad esperados para aplicaciones web que gestionan accesos operativos.

Se distingue claramente entre:

- hash: proceso de una sola vía para proteger la contraseña;
- cifrado: proceso reversible, que no se observa en este caso.

La diferencia es importante: el sistema no está cifrando contraseñas para poder recuperarlas después; lo que hace es protegerlas a través de hashes seguros. Este enfoque es apropiado para un sistema de autenticación web y es más seguro que almacenar credenciales en texto claro.

#### 2.7. Control de acceso según roles

DATALAN implementa un control de acceso basado en roles, no en permisos globales de Django por defecto. Los roles operativos se definen en [auth_service.py](../DATALAN/DATALAN/auth_service.py) dentro del diccionario `ROLES`, con claves como `admin`, `comercial`, `planta_encargado`, `tecnico`, `sistemas_encargado` y `soporte_sistemas`.

Cada usuario se asocia a un rol mediante `datalan.usuarios_roles`, mientras que la sesión almacena el rol actual del usuario autenticado. La autenticación asigna la identidad y el rol, y la aplicación luego controla el acceso a las vistas mediante decoradores.

El guardiano principal está en [views.py](../DATALAN/DATALAN/views.py):

```python
def current_user(request):
    return request.session.get('identity')


def protected(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not current_user(request):
            return redirect(f'/login/?next={request.path}')
        return view(request, *args, **kwargs)
    return wrapped


def admin_only(view):
    @wraps(view)
    @protected
    def wrapped(request, *args, **kwargs):
        if request.session.get('role') != 'admin':
            return redirect('access_denied')
        return view(request, *args, **kwargs)
    return wrapped
```

Esto significa que:

- si no existe identidad en sesión, la vista redirige al login;
- si el usuario no es administrador, el acceso a rutas de administración se redirige a `acceso-denegado`;
- para otras vistas, se valida la sesión y luego la lógica interna del flujo revisa el rol y la pantalla correspondiente;
- el usuario puede navegar solo a los módulos asociados a su rol y a los permisos activos.

La autorización suele revisarse dentro de `workflow()` y el contenido de navegación se filtra según el rol, por ejemplo con `enabled_modules_for_role(role_name, configured_modules)` y `navigation(...)` en [views.py](../DATALAN/DATALAN/views.py). Esta estrategia se interpreta como un control de acceso funcional basado en sesiones y roles, aunque no representa un sistema de permisos de Django con autenticación granular por objeto o por modelo.

### 3. Conclusión

El sistema DATALAN implementa mecanismos de seguridad relevantes y verificables para un entorno web de gestión operativa. La autenticación se realiza con un servicio propio que valida credenciales contra la base de datos, gestiona sesiones con Django y protege las contraseñas mediante hashing seguro con Argon2/PBKDF2. La sesión se configura para expirarse en 30 minutos, cerrar al salir del navegador y almacenar la identidad/rol del usuario autenticado. El proyecto también incorpora middleware de seguridad, control de CSRF, cookies HttpOnly, protección X-Frame-Options, HSTS y validación de complejidad de contraseñas.

No obstante, la revisión del repositorio no encontró evidencias de autenticación de dos factores, JWT, REST tokens, recuperación segura de contraseña o bloqueo por intentos fallidos. En otras palabras, DATALAN tiene una base sólida para la autenticación web y la autorización por roles, pero no implementa un modelo de seguridad avanzada para accesos sensibles, recuperación de credenciales ni prevención de ataques de fuerza bruta.

En términos académicos, la seguridad implementada es real y verificable, pero también es parcialmente limitada, funcional y adaptada al proyecto. La configuración de seguridad está presente, pero su nivel de madurez depende del entorno operativo y de la política de despliegue, especialmente en lo relacionado con HTTPS, cookies seguras y gestión de credenciales en producción.

### 4. Referencias bibliográficas

1. Django Software Foundation. Django documentation: Authentication. Disponible en: https://docs.djangoproject.com/en/6.1/topics/auth/
2. Django Software Foundation. Django documentation: Sessions. Disponible en: https://docs.djangoproject.com/en/6.1/topics/http/sessions/
3. Django Software Foundation. Django documentation: Security in Django. Disponible en: https://docs.djangoproject.com/en/6.1/topics/security/
4. Open Web Application Security Project (OWASP). Authentication Cheat Sheet. Disponible en: https://cheatsheetseries.owasp.org/cheatsheet/Authentication_Cheat_Sheet.html
5. OWASP. Password Storage Cheat Sheet. Disponible en: https://cheatsheetseries.owasp.org/cheatsheet/Password_Storage_Cheat_Sheet.html
6. OWASP. CSRF Prevention Cheat Sheet. Disponible en: https://cheatsheetseries.owasp.org/cheatsheet/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
7. OWASP. Session Management Cheat Sheet. Disponible en: https://cheatsheetseries.owasp.org/cheatsheet/Session_Management_Cheat_Sheet.html

### 5. Evidencias del repositorio analizadas

- [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)
- [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- [DATALAN/DATALAN/urls.py](../DATALAN/DATALAN/urls.py)
- [DATALAN/DATALAN/templates/login.html](../DATALAN/DATALAN/templates/login.html)
- [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py)

Este documento se elaboró a partir de la inspección del código fuente y la documentación del proyecto, sin modificar la lógica del sistema ni introducir cambios operativos adicionales.
