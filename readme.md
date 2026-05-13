 🐳 GHCR Simple API - CI/CD con GitHub Actions y Kubernetes

 API mínima en Flask para demostrar un pipeline completo de CI/CD: desde el `git push` hasta el despliegue en Kubernetes local usando GitHub
 Actions y un self-hosted runner.

 ## 📋 Requisitos previos

 - Docker Desktop con **Kubernetes activado**
 - `kubectl` configurado y funcionando (`kubectl get nodes`)
 - Repositorio público en GitHub
 - Self-hosted runner configurado en tu PC
 - https://github.com/{{Tu-user}}/{{Nombre-repo}}/settings/actions/runners/new

 ## 🚀 Flujo de CI/CD

 ```mermaid
 ```markdown
| Paso | Acción |
|------|--------|
| 1 | git push |
| 2 | GitHub Actions detecta el cambio |
| 3 | Construir imagen Docker |
| 4 | Subir imagen a GHCR |
| 5 | Conectar a clúster local (self-hosted runner) |
| 6 | Aplicar manifiestos Kubernetes |
| 7 | Reiniciar deployment |
```

 ## 📁 Estructura del proyecto

 ```
 GHCR-Simple-API/
 ├── .github/workflows/deploy.yml   # Pipeline CI/CD
 ├── k8s/
 │   └── simple-api.yaml            # Manifiestos de Kubernetes
 ├── app.py                         # API en Flask
 ├── Dockerfile                     # Crea imagen
 ├── requirements.txt               # Requisitos para la api
 └── README.md
 ```

 ## 🐍 API endpoints

 | Endpoint | Método | Respuesta |
 |----------|--------|-----------|
 | `/` | GET | Mensaje de bienvenida + nombre del pod |
 | `/health` | GET | Sonda de salud para Kubernetes |
 | `/ready` | GET | Sonda de readiness para Kubernetes |

 ## 🐳 Docker

 ### Construir imagen local

 ```bash
 docker build -t simple-api:latest .
 ```

 ### Ejecutar contenedor

 ```bash
 docker run -p 5000:5000 simple-api:latest
 ```

 ### Probar localmente

 ```bash
 curl http://localhost:5000/
 curl http://localhost:5000/health
 ```

 ## ☸️ Despliegue en Kubernetes

 ### Aplicar los manifiestos

 ```bash
 kubectl apply -f k8s/simple-api.yaml
 ```

 ### Ver recursos

 ```bash
 kubectl get all -n simple-api
 ```

 ### Probar la API desplegada

 ```bash
 curl http://localhost:30080/
 curl http://localhost:30080/health
 ```

 ### Limpiar recursos

 ```bash
 kubectl delete namespace simple-api
 ```

 ## 🔄 CI/CD con GitHub Actions

 El workflow `deploy.yml` hace:

 1. **Checkout** del código
 2. **Login** en GHCR (con `secrets.GHCR_PAT`)
 3. **Build** de la imagen Docker
 4. **Push** a GHCR
 5. **Conexión** al clúster local (via self-hosted runner)
 6. **Aplicación** de los manifiestos Kubernetes
 7. **Reinicio** del deployment

 ### Secretos necesarios

 | Secreto | Valor |
 |---------|-------|
 | `GHCR_PAT` | Personal Access Token con permiso `write:packages` |
 | `KUBECONFIG_BASE64` | `cat ~/.kube/config | base64` (opcional) |

 ## 🧪 Probar el pipeline

 ```bash
 git add .
 git commit -m "test: trigger pipeline"
 git push origin main
 ```

 ## ⚠️ Posibles problemas y soluciones

 ### 1. Error: `ImagePullBackOff` o `CrashLoopBackOff`

 **Causa**: El pod no puede descargar la imagen o la aplicación falla al arrancar.

 **Soluciones**:
 ```bash
 # Ver logs del pod
 kubectl logs <pod-name> -n simple-api

 # Ver logs del intento anterior (si el pod se reinicia)
 kubectl logs <pod-name> -n simple-api --previous

 # Describir el pod para ver eventos
 kubectl describe pod <pod-name> -n simple-api
 ```

 ### 2. Error: `failed to pull image` / `unauthorized`

 **Causa**: La imagen en GHCR es privada o el token no tiene permisos.

 **Soluciones**:
 ```bash
 # Hacer pública la imagen en GHCR (web)
 # O crear imagePullSecret en Kubernetes:
 kubectl create secret docker-registry ghcr-secret \
   --docker-server=ghcr.io \
   --docker-username=MarioAran \
   --docker-password=TU_PAT_TOKEN \
   --namespace=simple-api
 ```

 ### 3. Error: `connection refused` en `kubectl`

 **Causa**: Kubernetes no está activado o el kubeconfig es inválido.

 **Soluciones**:
 ```bash
 # Verificar conexión con kubeconfig específico

 #cuando se ejecuta el runner de github action suele romper kubeconfig se recomienda crear una copia y usarla para que el runner no tenga acceso al origina
 cat ~/.kube/config > /tmp/test-config
 KUBECONFIG=/tmp/test-config kubectl get nodes


 # Verificar que Docker Desktop tiene Kubernetes activado
 kubectl cluster-info
 ```

 ### 4. El runner no recoge los jobs

 **Causa**: El self-hosted runner no está ejecutándose.

 **Solución**:
 ```bash
 # Iniciar el runner manualmente ya que no es un servicio 
 cd actions-runner
 ./run.sh
 
 # Ver logs del runner
 tail -f runner.log
 
 # si lo quieres configurar como servicio usa el script svc.sh
 ./svc.sh install
 ./svc.sh start
 #comandos utiles 
 Comando	Acción
 ./svc.sh install	Instala el servicio launchd.
 ./svc.sh start	Inicia el servicio (el runner empieza a escuchar trabajos).
 ./svc.sh stop	Detiene el servicio.
 ./svc.sh status	Muestra si el servicio está activo o no.
 ./svc.sh uninstall	Elimina el servicio del sistema. 

 #si no sabes como obtener el runner ve a tu proyecto -> actions -> runner -> new runner -> new self-hosted runner y seguir las instrucciones 
 #en mi caso uso el selft hosted porque lo pruebo en un k8s local 
 ```

 ### 5. Error: `AssertionError: View function mapping is overwriting...`

 **Causa**: Dos funciones con el mismo nombre en `app.py` (Flask).

 **Solución**: Revisar que cada `@app.route` tenga una función diferente.

 ```python
 @app.route('/health')
 def health():  # ← principa
     return jsonify({"status": "healthy"}), 200

 @app.route('/ready')
 def ready():   # ← funcion con el mismo nombre 
     return jsonify({"status": "ready"}), 200
 ```

 ### 6. El workflow se queda en "Waiting for a runner"

 **Causa**: El self-hosted runner no está online.

 **Soluciones**:
 ```bash
 # 1. Verificar que el runner está ejecutándose
 ps aux | grep run.sh

 # 2. Reiniciar el runner
 cd actions-runner
 ./run.sh

 # 3. Verificar en GitHub: Settings → Actions → Runners
 # El estado debe ser "Idle"
 ```

 ## 📝 Notas

 - El self-hosted runner debe estar ejecutándose (`./run.sh`)
 - El paquete en GHCR debe ser **público** o tener `imagePullSecret`
 - Kubernetes debe estar activado en Docker Desktop

 ## 📬 Contacto

 - **GitHub**: [@MarioAran](https://github.com/MarioAran)
 - **Email**: arancibiagm@gmail.com

 ---

 🚀 *Proyecto creado como parte del portfolio de DevOps en formación.*