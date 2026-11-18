# Auditoría de seguridad de DATALAN (solo lectura)

## Alcance y método

Esta auditoría se ha realizado sin modificar código, configuración, dependencias ni datos del proyecto. Se ha basado en lectura de archivos del repositorio y en la revisión de pruebas existentes, sin ejecutar migraciones ni operaciones que alteren la base de datos.

Archivos revisados:
- [requirements.txt](../requirements.txt)
- [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)
- [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- [DATALAN/DATALAN/urls.py](../DATALAN/DATALAN/urls.py)
- [DATALAN/DATALAN/templates/login.html](../DATALAN/DATALAN/templates/login.html)
- [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py)

---

## 1) Contraseñas: algoritmo efectivo, parámetros, diferencia entre nuevos hashes y formatos antiguos

### 1.1. Evidencia revisada

La lógica de creación y verificación se encuentra en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py):

```python
from django.contrib.auth.hashers import check_password, make_password
...
password_valid = check_password(password, stored_password)
...
if not password_valid and stored_password == password:
    password_valid = True
    stored_password = make_password(password)
    cursor.execute(
        'UPDATE datalan.usuarios SET password_hash = %s WHERE user_id = %s',
        [stored_password, user_id],
    )
```

La creación de nuevas cuentas usa:

```python
INSERT INTO datalan.usuarios
    (username, full_name, email, identity_number, password_hash)
VALUES (%s, %s, %s, %s, %s)
```

con el valor `make_password(user_data['password'])` en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py).

### 1.2. Qué puede confirmarse a partir del código

- La aplicación usa Django hashers a través de `make_password` y `check_password`.
- No se declara `PASSWORD_HASHERS` explícitamente en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py).
- En Django 5.2, si no se sobrescribe la configuración, el hasher por defecto de Django es el algoritmo `PBKDF2` con el hasher `PBKDF2PasswordHasher` y el valor de iteraciones por defecto del framework (en Django 5.2 es un valor del hasher PBKDF2, no un valor aleatorio arbitrario del proyecto).
- El hasher incluye un salt aleatorio por contraseña nueva. Ese salt no se puede afirmar con lectura del código sin inspeccionar el valor generado ni la base de datos real.

### 1.3. Qué no puede confirmarse con esta auditoría

No se puede afirmar de forma demostrada el algoritmo efectivo real de las contraseñas nuevas en producción o en la base de datos del proyecto, porque faltan las siguientes evidencias:

- configuración efectiva del entorno de ejecución,
- contenido real del campo `password_hash` en la base de datos,
- una inspección de `PASSWORD_HASHERS` en el entorno ejecutado,
- una comprobación del hasher activo en la instancia real.

Por tanto, la conclusión correcta es:

- Hay evidencia de uso de `make_password`/`check_password` y de la configuración por defecto de Django.
- No se ha podido confirmar el algoritmo efectivo real de todas las contraseñas nuevas del entorno de despliegue sin revisar la configuración ejecutada y los valores generados en la base de datos.

### 1.4. Formatos antiguos y contraseñas heredadas

La comprobación es explícita en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py):

```python
if not password_valid and stored_password == password:
    password_valid = True
    stored_password = make_password(password)
```

Esto indica:

- existía la posibilidad de que una contraseña antigua se almacenara de un formato no seguro o no estándar,
- la aplicación intenta detectar el caso en el que el valor existente sea texto plano,
- y entonces lo convierte a un hasher de Django para que la próxima validación use el algoritmo actual del framework.

La diferencia clave es:

- para contraseñas nuevas el flujo esperado es un hash del hasher activo,
- para formatos antiguos puede haber texto plano o cualquier valor antiguo que coincida exactamente con la cadena introducida,
- la auditoría no tiene evidencia de que el proyecto haya revisado y migrado todos los registros antiguos en la base de datos.

### 1.5. Conclusión técnica

La afirmación correcta no es “se sabe exactamente qué hash usan todas las contraseñas del sistema”, sino:

- el código usa `make_password`/`check_password`,
- el patrón más probable para contraseñas nuevas es el hasher por defecto de Django 5.2,
- los formatos antiguos no quedan demostrados por la auditoría porque no se inspeccionó el contenido real almacenado ni la configuración ejecutada.

---

## 2) `AUTH_PASSWORD_VALIDATORS`: cuándo se aplican y dónde realmente se invocan

### 2.1. Configuración declarada

La configuración aparece en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py):

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### 2.2. Dónde realmente se invoca

Se localiza una invocación real en el flujo de creación de usuario, en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py):

```python
validate_email(user_data['email'])
from django.contrib.auth.password_validation import validate_password
validate_password(user_data['password'])
```

Esto pertenece a la vista `user_create` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).

### 2.3. No se exige ejecutar en cada login

La autenticación real del login no llama a `validate_password` ni a `AUTH_PASSWORD_VALIDATORS` en la función `authenticate` de [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py). La comprobación de contraseña se realiza con `check_password`, no con la validación de políticas de contraseña.

Esto significa:

- la política existe en configuración,
- se aplica en ciertos flujos de alta/creación de cuentas,
- pero no se exige ejecutarla en cada intento de autenticación.

### 2.4. Flujos existentes revisados

Se han localizado estos flujos:

- creación de nueva cuenta en `user_create` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- validación de correo y contraseña en el mismo flujo [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- no se localizó un flujo de cambio de contraseña ni de recuperación de contraseña dentro del alcance revisado en la capa de aplicación principal

### 2.5. Conclusión

La correcta formulación es:

- `AUTH_PASSWORD_VALIDATORS` está configurado en la aplicación.
- Se invoca activamente en la creación de usuarios y en la validación del formulario de alta.
- No se evidencia que la aplicación llame a esos validadores en cada login o en cada cambio de contraseña, porque la autenticación principal usa `check_password` y no una validación de reglas de contraseña.

---

## 3) Valores efectivos de cookies y seguridad de sesión

### 3.1. Evidencia revisada

En [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py) no aparecen valores explícitos para los siguientes ajustes:

- `SESSION_COOKIE_SECURE`
- `SESSION_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- `SESSION_COOKIE_AGE`
- `SESSION_EXPIRE_AT_BROWSER_CLOSE`
- `CSRF_COOKIE_SECURE`
- `SECURE_SSL_REDIRECT`

La única configuración de sesión explícita es:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```

### 3.2. Qué sí se puede concluir

- En este archivo, los valores no están declarados explícitamente.
- Eso no equivale a afirmar que estén desactivados ni que el despliegue los haya sobrescrito.
- El efecto real depende del entorno de ejecución y de la configuración final del despliegue, que no se ha inspeccionado en esta auditoría de solo lectura.

### 3.3. Valores predeterminados de Django (solo como referencia de configuración del framework)

Django usa valores por defecto si no se declaran. Es importante distinguir estos valores por defecto de los valores concretos del proyecto revisado:

- `SESSION_COOKIE_HTTPONLY` suele ser `True` por defecto en Django moderno.
- `SESSION_COOKIE_SAMESITE` suele tener el valor `'Lax'` por defecto en versiones recientes.
- `SESSION_COOKIE_SECURE` suele ser `False` por defecto.
- `SESSION_COOKIE_AGE` tiene un valor por defecto del framework.
- `SESSION_EXPIRE_AT_BROWSER_CLOSE` suele ser `False` por defecto.
- `CSRF_COOKIE_SECURE` suele ser `False` por defecto.
- `SECURE_SSL_REDIRECT` suele ser `False` por defecto.

Pero estos valores no son una comprobación del despliegue real; son el comportamiento estándar del framework si no se reconfiguran.

### 3.4. Conclusión

La evidencia real disponible es:

- la aplicación no declara estos ajustes explícitamente en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py),
- por tanto, no puede afirmarse que el proyecto esté reforzando estos parámetros de seguridad en la configuración revisada,
- tampoco puede afirmarse que estén desactivados en producción sin inspeccionar la configuración de despliegue real.

---

## 4) Sesiones con cookies firmadas: firma frente a cifrado, contenido guardado, expiración y revocación

### 4.1. Configuración observada

La aplicación usa:

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```

en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py).

### 4.2. Firma vs cifrado

Este backend firma la sesión con la clave secreta del proyecto. No es lo mismo que cifrado:

- firma: permite verificar que el contenido no ha sido alterado por un tercero que conozca la clave,
- cifrado: protege el contenido contra lectura por terceros que no tienen la clave.

Un backend de cookies firmadas guarda datos de la sesión en el propio valor de la cookie, y la firma evita alteraciones maliciosas de ese contenido sin ocultarlo totalmente a quien la vea.

### 4.3. Contenido guardado y sesión manual

La aplicación guarda sesión manualmente en las vistas:

```python
request.session.cycle_key()
request.session['identity'] = identity
request.session['role'] = identity['role']
```

y se recupera con:

```python
return request.session.get('identity')
```

Esto pertenece a [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py) y a [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).

### 4.4. `cycle_key()` y `flush()`

En el código revisado:

```python
request.session.cycle_key()
```

se usa durante el login. La función `cycle_key()` del backend de Django rota la clave de la sesión y ayuda a mitigar fijación de sesión. Es una medida útil, pero no equivale a una política completa de revocación de sesiones anteriores.

Por otro lado:

```python
request.session.flush()
```

se usa en el logout. Esto elimina la sesión actual del almacenamiento activo. Sin embargo, en un backend de cookies firmadas, la evidencia no demuestra una revocación efectiva de todas las copias de la cookie que pudieran existir previamente en un navegador o en un cliente no seguro.

### 4.5. Reutilización de una cookie anterior tras logout, cambio de contraseña, cambio de rol o desactivación

La auditoría no encontró un mecanismo explícito que revise y rechace una sesión antigua tras:

- logout,
- cambio de contraseña,
- cambio de rol,
- desactivación de la cuenta.

Lo observado es:

- `flush()` en logout,
- `cycle_key()` en login,
- almacenamiento manual en `request.session['role']` y `request.session['identity']`.

Pero no aparece un mecanismo de invalidación por identidad, contraseña o rol en la lógica de sesión. Por tanto, no se puede afirmar que exista revocación efectiva de una sesión anterior solo por haber encontrado `flush()`; eso sería una conclusión más fuerte que la evidencia revisada.

### 4.6. Conclusión

Se puede afirmar que:

- hay una sesión basada en cookies firmadas,
- hay rotación de sesión en login,
- hay limpieza en logout,
- pero no hay evidencia verificable de revocación robusta tras cambios de contraseña, rol o desactivación.

Esto queda pendiente y no debe presentarse como fallo demostrado si la auditoría no lo ejecuta en un entorno real.

---

## 5) Condición completa del fallback `stored_password == password`

### 5.1. Código revisado

La condición completa está en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py):

```python
password_valid = check_password(password, stored_password)
if not password_valid and stored_password == password:
    password_valid = True
    stored_password = make_password(password)
    cursor.execute(
        'UPDATE datalan.usuarios SET password_hash = %s WHERE user_id = %s',
        [stored_password, user_id],
    )
```

### 5.2. Qué hace exactamente

La condición se activa si:

- la validación normal falla, y
- el valor almacenado es exactamente igual a la cadena introducida por el usuario.

Esto hace dos cosas importantes:

1. detecta el caso de una contraseña antigua almacenada en texto plano,
2. acepta como válida la misma cadena que existe en la base de datos.

### 5.3. ¿Puede aceptar también el propio hash almacenado?

Sí, puede aceptarlo en principio, si el valor introducido como `password` es exactamente la misma cadena que estaba almacenada en el campo de la base de datos.

Esto significa que, si un atacante o usuario conoce el valor hash almacenado y lo introduce como contraseña en la UI, la condición `stored_password == password` puede evaluarse como verdadera cuando el valor del campo almacenado coincide con el valor introducido. Es un riesgo de lógica de comparación textual, no una suposición sobre cuentas reales.

### 5.4. Alcance de la condición

La evidencia no demuestra que un usuario real pueda encontrar esa coincidencia en la práctica sin acceso previo al almacenado. Pero sí demuestra que el flujo de autenticación no distingue entre:

- texto plano,
- hash reconocido,
- valor de texto exacto coincidente con el campo almacenado.

Esto debe considerarse un fallo potencial de lógica de comparación, no un fallo explotado demostrable con cuentas reales.

---

## 6) Rol `admin`: funciones, acceso y relación con los cinco roles operativos

### 6.1. Definición del rol

El rol `admin` se define en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py):

```python
ROLES = {
    'admin': {
        'label': 'Administrador',
        'home': '/',
        'modules': [...]
    },
    'comercial': {...},
    'planta_encargado': {...},
    'tecnico': {...},
    'sistemas_encargado': {...},
    'soporte_sistemas': {...},
}
```

### 6.2. Control de acceso real observado

El acceso se hace con un decorador personalizado:

```python
@admin_only
```

y la comprobación es:

```python
if request.session.get('role') != 'admin':
    return redirect('access_denied')
```

Esto aparece en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).

### 6.3. Funciones de administrador revisadas

Se localizan funciones admin-only en:

- `users` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `user_create` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `toggle_user` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `user_delete` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `roles_access` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `admin_records` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `admin_system_register` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 6.4. Relación con los cinco roles operativos

Los cinco roles del informe están definidos como roles operativos distintos del administrador:

- `comercial`
- `planta_encargado`
- `tecnico`
- `sistemas_encargado`
- `soporte_sistemas`

El `admin` no es un “superuser” de Django; es un rol propio del negocio, con su propia entidad en el diccionario `ROLES` y su verificación manual en la sesión.

### 6.5. Permisos por registro y asignación

La revisión concreta muestra que la autorización basada en sesión se usa en varias operaciones, por ejemplo:

- `workflow` permite acceso solo si `request.session.get('role') == role_name` y el módulo está habilitado, en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).
- `update_technician_profile` y `update_incident_technician_profile` requieren el rol `planta_encargado` para permitir cambios, en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).
- la lógica de técnico asignado en `workflow` compara el nombre autenticado con los técnicos asignados al registro, en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).

Esto muestra comprobaciones por registro y por valor del registro, pero no una ACL por fila con restricciones de base de datos. La ausencia de una capa formal de ACL no es una prueba de autorización insuficiente por sí sola; sí es una limitación de la evidencia revisada.

### 6.6. Caso especial “Sistemas puede coordinar un trabajo cuando está asignado como Soporte”

La revisión no encontró una regla de autorización basada en una tabla especial ni en un permiso explícito por objeto; lo que sí se observa es una combinación de:

- rol actual en sesión,
- asignación del trabajo,
- navegación por módulos habilitados,
- validación en la pantalla.

Esto debe tratarse como una comprobación funcional del código, no como una prueba concluyente de separación formal de responsabilidades en todos los permisos del sistema.

---

## 7) SQL parametrizado, CSRF, XSS y validación del servidor

### 7.1. SQL parametrizado

Se encontraron ejemplos de SQL parametrizado en la lógica de autenticación y administración. Por ejemplo:

```python
cursor.execute("""
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
""", [username.strip(), username.strip()])
```

También existen patrones parametrizados en:

- `create_registered_user` [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- `roles_access` [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- usuario y permisos [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 7.2. Importante: no generalizar a todo el sistema

La auditoría no encontró evidencia suficiente para afirmar que todas las consultas del proyecto están parametrizadas de forma segura, ni para afirmar lo contrario sin una revisión completa por módulo.

Lo correcto es:

- hay evidencia de consultas parametrizadas en varios flujos clave,
- pero no se generaliza a toda la base de código sin una revisión integral por cada operación SQL.

### 7.3. CSRF

La presencia del middleware y del token en formularios es visible en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py) y en [DATALAN/DATALAN/templates/login.html](../DATALAN/DATALAN/templates/login.html):

```html
<form method="post">{% csrf_token %}
```

También se observan `{% csrf_token %}` en formularios relevantes en varias plantillas. Eso demuestra presencia del control en la interfaz, pero no prueba de forma concluyente que cada acción crítica del sistema lo aplique de forma efectiva en todos los flujos o en todas las peticiones AJAX, porque esto requeriría una revisión de cada endpoint y una ejecución real con el navegador.

### 7.4. XSS

La auditoría no encontró un uso directo de `mark_safe` ni de HTML sin escapar en la capa Python revisada. Django templates utilizan autoescape por defecto, y hay uso del helper `escape(...)` en generación de PDF y texto de reportes en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py).

Sin embargo, no se puede concluir que todo el sistema está libre de XSS sin una revisión exhaustiva de:

- JS cliente,
- inserción dinámica de HTML,
- render de contenido no escapado,
- peticiones AJAX,
- HTML generado en plantillas secundarias.

### 7.5. Validación del servidor

La validación de servidor se observa en varios puntos:

- `validate_email` y `validate_password` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- `require_POST` en varios controladores, por ejemplo [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- comprobaciones de rol antes de ejecutar cambios o consultas sensibles en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

No obstante, eso no demuestra que todas las operaciones sensibles estén protegidas de forma uniforme. La auditoría observó validación en ciertos flujos clave, no en todos los endpoints.

---

## 8) Evidencias exactas por hallazgo, función y líneas

### 8.1. Autenticación personalizada

- Función: `authenticate` en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- Rango relevante: `authenticate` y la rama legacy `stored_password == password`
- Evidencia: SQL directo contra `datalan.usuarios`, `datalan.usuarios_roles`, `datalan.roles` y uso de `check_password`

### 8.2. Sesiones y cookies firmadas

- Configuración: [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)
- Funciones: `login_view`, `logout_view` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- Evidencia: `SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'`, `request.session.cycle_key()`, `request.session.flush()`

### 8.3. Hash y validación de contraseña

- Archivo: [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- Evidencia: `check_password`, `make_password`, fallback `stored_password == password`

### 8.4. Validadores de contraseña

- Configuración: [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)
- Invocación: `user_create` y `validate_password` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 8.5. Permisos por rol y acceso directo

- Controladores: `protected`, `admin_only`, `workflow`, `update_technician_profile`, `update_incident_technician_profile` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- Evidencia: comprobaciones `request.session.get('role')` y redirección a `access_denied`

### 8.6. Tests existentes

- Archivo: [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py)
- Clases: `Iteration1PostgreSQLTests`
- Casos clave: `test_i1_01_login_role_destinations_and_rejected_credentials` y `test_i1_02_server_permission_for_profile_reads_and_updates`
- Comentario: existen y son relevantes para la auditoría, pero no se ejecutaron en esta revisión por requerimiento de solo lectura.

---

## 9) Fragmentos breves para figuras / evidencias del trabajo

### 9.1. Autenticación y sesión

```python
if request.method == 'POST':
    identity = authenticate(
        request.POST.get('username', ''),
        request.POST.get('password', ''),
    )
    if identity:
        request.session.cycle_key()
        request.session['identity'] = identity
        request.session['role'] = identity['role']
        return redirect(ROLES[identity['role']]['home'])
```

Archivo: [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 9.2. Configuración de sesiones

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
```

Archivo: [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)

### 9.3. Fallback de contraseña heredada

```python
password_valid = check_password(password, stored_password)
if not password_valid and stored_password == password:
    password_valid = True
    stored_password = make_password(password)
```

Archivo: [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)

### 9.4. Permisos por rol

```python
@admin_only
def user_create(request):
    ...
```

```python
if request.session.get('role') != 'planta_encargado':
    return redirect('access_denied')
```

Archivos: [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 9.5. Validadores de contraseña

```python
from django.contrib.auth.password_validation import validate_password
validate_password(user_data['password'])
```

Archivo: [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)

### 9.6. Tests relevantes

```python
def test_i1_01_login_role_destinations_and_rejected_credentials(self):
    ...
    self.assertContains(response, 'Usuario, contraseña incorrectos')
```

Archivo: [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py)

### 9.7. Capturas sugeridas para la actividad

Se recomienda capturar estas pantallas o fragmentos con ocultación de datos sensibles:

- formulario de login y token CSRF en [DATALAN/DATALAN/templates/login.html](../DATALAN/DATALAN/templates/login.html)
- definición de `SESSION_ENGINE` en [DATALAN/DATALAN/settings.py](../DATALAN/DATALAN/settings.py)
- función `authenticate` en [DATALAN/DATALAN/auth_service.py](../DATALAN/DATALAN/auth_service.py)
- comprobación de `role` y `access_denied` en [DATALAN/DATALAN/views.py](../DATALAN/DATALAN/views.py)
- test de login y permisos en [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py)

No se deben incluir contraseñas reales, hashes reales, cookies reales ni datos personales.

---

## 10) Síntesis final académica

### 10.1. Seguridad de inicio de sesión y sesiones

El proyecto presenta un flujo de autenticación personalizado basado en validación manual de credenciales y sesión en cookies firmadas. La lógica real de acceso no usa el backend estándar de Django para el caso principal del negocio, sino una función `authenticate` con SQL directo y comprobación por sesión. La sesión se maneja con `request.session` y el backend `signed_cookies`, con rotación en login y limpieza en logout. Sin embargo, la auditoría no encontró evidencia suficiente de políticas adicionales como bloqueo por intentos, levantamiento de sesión segura por configuración explícita o revocación robusta tras cambios de contraseña o rol. Esos elementos quedan como pendientes y no deben entenderse como implementados.

### 10.2. Manejo de contraseñas

La aplicación usa `make_password` y `check_password`, por lo que hay evidencia clara de uso de hash de Django. No obstante, la lógica incorpora un fallback que compara la contraseña almacenada con el valor introducido en texto plano y, si coincide, rehashea la contraseña. Eso revela una migración de credenciales heredadas que no puede considerarse completamente segura ni completamente documentada sin revisar los datos reales almacenados y la configuración del entorno. La diferencia entre formatos nuevos y antiguos queda documentada como un punto de riesgo potencial y no como fallo explotado demostrado.

### 10.3. Prácticas de desarrollo seguro, protección de datos y amenazas

La aplicación presenta indicadores de seguridad en la capa de formularios y middleware (`CsrfViewMiddleware`, `{% csrf_token %}`, `SecurityMiddleware`), así como validaciones de creación de usuarios. Sin embargo, no se verificó una configuración robusta del despliegue para cookies, sesión, HTTPS o hardening. Además, la ausencia de ACL explícita por objeto y el uso de una sesión manual por rol no equivalen a una base de autorización formal completa. La auditoría distingue entre controles presentes en código y controles verificados en ejecución; en este caso, la implementación funcional básica está presente, pero los controles de despliegue y revocación no pueden asumirse como completos.

### 10.4. Pruebas y limitaciones

Los tests revisados existen en [DATALAN/DATALAN/test_iteration1.py](../DATALAN/DATALAN/test_iteration1.py); cubren parcialmente login y permisos por perfil. No se ejecutaron en esta auditoría por requerimiento de solo lectura. Esto limita la fuerza de la evidencia: los tests validan comportamiento funcional básico, pero no sustituyen una revisión de seguridad real ni una verificación de despliegue con datos reales. Por ello, las conclusiones deben mantenerse en el nivel de análisis estático: se confirma lo que el código contiene, y se deja como pendiente lo que no puede verificarse sin entorno y ejecución.

### 10.5. Cierre académico

La conclusión correcta para una actividad universitaria es la siguiente:

- el proyecto implementa un mecanismo funcional de autenticación y autorización básico;
- presenta uso de hash en contraseñas y validación de formularios;
- incorpora sesión y protección CSRF en varios puntos;
- pero no puede declararse como una implementación segura de producción sin controles adicionales, revisión de entorno real y validación ejecutada.

Los controles pendientes, no implementados ni verificados a nivel real, son:

- migración fuerte de contraseñas heredadas,
- hardening de cookies y sesión,
- bloqueo por intentos y MFA,
- revisión completa de ACL por objeto,
- validación real del entorno de despliegue,
- y comprobación de evolución de sesiones tras cambios de contraseña, rol o desactivación.

---

## Conclusión final

La auditoría estática confirma que el proyecto tiene un flujo funcional de login, rol y permisos. También confirma que la aplicación usa hashing de Django y una sesión en cookies firmadas, así como validadores de contraseña en ciertos flujos de alta. Pero la evidencia no permite afirmar que exista un sistema robusto de seguridad, ni que todas las medidas de protección se hayan implementado y verificado en la instancia real. La conclusión adecuada para la actividad es una formulación de riesgo y evidencia: el proyecto tiene controles básicos y un diseño funcional, pero requiere revisión adicional para escenarios de producción y no debe presentarse como una implementación segura certificada ni completamente validada.
