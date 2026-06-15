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
```
# Aplicar los manifiestos
kubectl apply -f k8s/simple-api.yaml

# Ver recursos
kubectl get all -n simple-api

# Hacer port-forward
kubectl port-forward service/simple-api-service 30080:5000 -n simple-api

# Probar la API desplegada
curl http://localhost:30080/
curl http://localhost:30080/health

# Limpiar
kubectl delete namespace simple-api
```

 ## 🔄 CI/CD con GitHub Actions

 El workflow `deploy.yml` hace:

1. Checkout: Clona el repositorio en el runner de GitHub Actions.

2. Login en GHCR: Se autentica en GitHub Container Registry usando un token (secrets.GHCR_PAT).

3. Build: Construye la imagen Docker de la aplicación.

4. Push: Sube la imagen a GHCR con una etiqueta (normalmente latest o el commit SHA).

5. Actualización del manifiesto (opcional): Si el pipeline actualiza el tag de la imagen en el repositorio Git (ej. :latest o un SHA específico), ArgoCD detectará el cambio en el manifiesto.

6. Detección por ArgoCD: ArgoCD, que monitoriza el repositorio Git, detecta el cambio en el manifiesto (por ejemplo, un nuevo tag de imagen o un cambio en el número de réplicas).

7. Sincronización automática (o manual): ArgoCD sincroniza el estado del clúster con el estado definido en Git.

8. Rolling update: Kubernetes realiza una actualización progresiva (rolling update), destruyendo los pods antiguos y creando nuevos con la versión actualizada de la imagen.

 ### Secretos necesarios

 | Secreto | Valor |
 |---------|-------|
 | `GHCR_PAT` | Personal Access Token con permiso `write:packages` |


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


 ### 3. ArgoCD no detecta cambios 

Causa: La sincronización automática no está activada o el webhook no está configurado.

Soluciones:
```
# Verificar que el app esté configurada con `syncPolicy: automated`
kubectl describe application simple-api -n argocd
```

 ### ArgoCD no detecta cambios
 Causa: La sincronización automática no está activada.

 Soluciones: Configurar en el Application:
 ```
 syncPolicy:
  automated:
    prune: true
    selfHeal: true
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
