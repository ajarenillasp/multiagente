# Guía de Instalación Detallada

## Sistema Multi-Agente para Jetson Thor

Esta guía te llevará paso a paso desde la instalación hasta tener el sistema funcionando con acceso remoto vía Cloudflare Tunnel.

---

## 📋 Prerrequisitos

### Hardware
- **Jetson Thor** con JetPack instalado
- Al menos 32GB RAM recomendado (para modelos grandes)
- GPU NVIDIA con drivers actualizados

### Software
- Docker instalado
- Docker Compose instalado
- Cuenta de Cloudflare (gratuita)

### Verificar instalación de Docker

```bash
docker --version
docker compose version
nvidia-smi  # Verificar que detecta la GPU
```

---

## 🚀 Paso 1: Clonar el Repositorio

```bash
cd ~
git clone <URL_DE_TU_REPOSITORIO>
cd multiagent-system
```

---

## 🤖 Paso 2: Configurar Ollama y Descargar Modelos

### Iniciar solo Ollama primero

```bash
cd ~/multiagent-system
docker compose up -d ollama
```

### Esperar a que Ollama esté listo (30 segundos)

```bash
docker logs ollama
```

### Descargar modelos recomendados

**IMPORTANTE**: Esto puede tardar bastante dependiendo de tu conexión.

```bash
# Modelo principal para análisis complejo (70B parámetros)
docker exec -it ollama ollama pull llama3:70b

# Modelo para código (34B parámetros)
docker exec -it ollama ollama pull codellama:34b

# Modelo rápido para tareas simples (7B parámetros)
docker exec -it ollama ollama pull mistral:7b

# Opcional: Modelo para análisis de imágenes
docker exec -it ollama ollama pull llava:13b
```

**Nota sobre espacio en disco**: 
- llama3:70b ≈ 40GB
- codellama:34b ≈ 20GB
- mistral:7b ≈ 4GB
- llava:13b ≈ 8GB

Total aproximado: **72GB**

Si tienes espacio limitado, comienza solo con `mistral:7b` y descarga los otros después.

### Verificar modelos instalados

```bash
docker exec -it ollama ollama list
```

Deberías ver algo como:
```
NAME              ID           SIZE      MODIFIED
llama3:70b        ...          40 GB     Now
codellama:34b     ...          20 GB     Now
mistral:7b        ...          4 GB      Now
```

---

## ☁️ Paso 3: Configurar Cloudflare Tunnel

### 3.1 Crear tunnel en Cloudflare

1. Ve a [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navega a **Zero Trust** → **Networks** → **Tunnels**
3. Click en **Create a tunnel**
4. Elige **Cloudflared** como tipo
5. Ponle nombre: `thor-agent`
6. Guarda las credenciales que te dan

### 3.2 Obtener token del tunnel

En la página de configuración del tunnel:

1. Click en **Install and run connector**
2. Elige **Docker** como entorno
3. Copia el **tunnel ID** y el **token**

### 3.3 Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
nano .env
```

Contenido:
```env
TUNNEL_ID=tu-tunnel-id-aqui
TUNNEL_TOKEN=tu-tunnel-token-aqui
```

Guarda con `Ctrl+X`, luego `Y`, luego `Enter`.

### 3.4 Configurar hostname

Edita el archivo de configuración:

```bash
nano docker/cloudflared/config.yml
```

Actualiza los hostnames:
```yaml
ingress:
  - hostname: thor-agent.tudominio.com  # Cambia por tu dominio o usa trycloudflare.com
    service: http://frontend:3000
  
  - hostname: thor-api.tudominio.com
    service: http://backend:8000
```

**Opción gratuita**: Si no tienes dominio, Cloudflare te dará un subdominio gratuito tipo `thor-agent.trycloudflare.com`

---

## 🔧 Paso 4: Ajustes Específicos para Jetson Thor

### 4.1 Verificar soporte GPU

El Jetson Thor tiene GPU integrada. Asegúrate de que Docker pueda acceder a ella:

```bash
# Verificar que el runtime nvidia está disponible
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

Deberías ver información de tu GPU.

### 4.2 Optimizar para Jetson (opcional pero recomendado)

Para mejor rendimiento en Jetson, edita `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Añade esta sección al servicio de Ollama si tienes problemas de memoria:

```yaml
  ollama:
    # ... resto de configuración
    environment:
      - OLLAMA_NUM_PARALLEL=1  # Limitar instancias paralelas
      - OLLAMA_MAX_LOADED_MODELS=1  # Un modelo a la vez
```

---

## ▶️ Paso 5: Iniciar Todo el Sistema

### 5.1 Construir e iniciar todos los servicios

```bash
cd ~/multiagent-system
docker compose build
docker compose up -d
```

### 5.2 Verificar que todo esté corriendo

```bash
docker compose ps
```

Deberías ver 4 servicios:
- `ollama` - Puerto 11434
- `multiagent-backend` - Puerto interno 8000
- `multiagent-frontend` - Puerto interno 3000
- `cloudflared` - Sin puertos expuestos

### 5.3 Ver logs

```bash
# Ver logs de todos
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f cloudflared
```

---

## 🌐 Paso 6: Acceder a la Interfaz Web

### 6.1 URL de acceso

Una vez que Cloudflare Tunnel esté conectado:

1. Ve a Cloudflare Dashboard → Zero Trust → Tunnels
2. Selecciona tu tunnel `thor-agent`
3. Verás el estado **Healthy**
4. La URL será la que configuraste (ej: `https://thor-agent.tudominio.com`)

### 6.2 Acceso directo (sin tunnel temporalmente)

Si quieres probar sin Cloudflare:

```bash
# Exponer frontend localmente
docker compose up -d frontend

# Acceder desde tu red local
http://<IP_DE_TU_JETSON>:3000
```

---

## 📝 Paso 7: Primer Uso

1. **Abre la interfaz web** en tu navegador
2. **Sube documentos** de requisitos (PDF, DOCX, MD, imágenes)
3. **Describe tu proyecto** en el campo de texto
4. **Selecciona el tipo**: Propuesta Europea o Código
5. **Click en "Analizar Proyecto"**
6. **Revisa la configuración** de agentes propuesta
7. **Ajusta modelos** si es necesario
8. **Confirma y ejecuta**
9. **Espera** a que se complete el proceso
10. **Descarga el resultado**

---

## ⚙️ Configuración Avanzada

### Cambiar directorio de input/output

Los documentos se guardan en:
- Input: `~/multiagent-system/input_docs/`
- Output: `~/multiagent-system/output_docs/`

Puedes acceder directamente:

```bash
ls ~/multiagent-system/input_docs/
ls ~/multiagent-system/output_docs/
```

### Monitorear uso de recursos

```bash
# Uso de GPU
tegrastats

# Uso de memoria
watch -n 1 free -h

# Logs en tiempo real
docker compose logs -f
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker compose restart

# Reiniciar un servicio específico
docker compose restart backend
```

### Actualizar modelos

```bash
# Ver modelos disponibles para actualizar
docker exec -it ollama ollama list

# Actualizar un modelo
docker exec -it ollama ollama pull llama3:70b
```

---

## 🛠️ Solución de Problemas

### Problema: Ollama no inicia

**Síntoma**: `docker compose ps` muestra ollama comoExited`

**Solución**:
```bash
# Ver logs de error
docker logs ollama

# Posible causa: falta GPU
# Verifica que tengas drivers NVIDIA actualizados
sudo apt update
sudo apt upgrade

# Reinicia Docker
sudo systemctl restart docker
```

### Problema: Memoria insuficiente

**Síntoma**: El sistema se congela o los procesos mueren

**Solución**:
1. Usa solo modelos pequeños inicialmente (mistral:7b)
2. Limita modelos cargados simultáneamente en config de Ollama
3. Cierra otras aplicaciones

### Problema: Cloudflare Tunnel no conecta

**Síntoma**: Estado del tunnel es "Disconnected"

**Solución**:
```bash
# Ver logs de cloudflared
docker logs cloudflared

# Verificar token
cat .env

# Regenerar token si es necesario
# Ve a Cloudflare Dashboard y genera uno nuevo
```

### Problema: API no responde

**Síntoma**: Error 502 o timeout

**Solución**:
```bash
# Verificar que backend esté corriendo
docker compose ps backend

# Ver logs del backend
docker compose logs backend

# Reiniciar backend
docker compose restart backend

# Verificar conexión con Ollama
docker exec -it multiagent-backend curl http://ollama:11434/api/tags
```

---

## 📊 Rendimiento Esperado

### Tiempos de generación (aproximados)

| Tipo | Modelo | Tiempo |
|------|--------|--------|
| Análisis inicial | llama3:70b | 2-5 min |
| Agente especialista | mistral:7b | 1-3 min |
| Agente especialista | llama3:70b | 3-8 min |
| Verificación (x5) | llama3:70b | 10-20 min |
| Edición final | mistral:7b | 1-2 min |

**Total estimado**: 15-40 minutos por proyecto completo

### Uso de recursos

- **RAM**: 16-32GB durante picos
- **GPU**: 50-80% usage
- **CPU**: 20-40% usage
- **Disco**: 72GB+ para modelos

---

## 🔒 Seguridad

### Mejores prácticas

1. **Mantén actualizado**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. **Firewall**:
   ```bash
   # Solo permite puertos necesarios
   sudo ufw allow 22/tcp  # SSH
   sudo ufw enable
   ```

3. **No expongas puertos directamente**: Usa siempre Cloudflare Tunnel

4. **Actualiza regularmente**:
   ```bash
   cd ~/multiagent-system
   git pull
   docker compose down
   docker compose build
   docker compose up -d
   ```

---

## 📞 Soporte

### Logs para debugging

```bash
# Recopilar todos los logs
docker compose logs > system_logs.txt

# Información del sistema
tegrastats --log jetson_stats.txt &
sleep 10
kill %1
```

### Comandos útiles

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes no usadas
docker image prune

# Ver uso de disco
docker system df

# Reset completo (CUIDADO: borra datos)
docker compose down -v
```

---

## ✅ Checklist Final

- [ ] Docker y Docker Compose instalados
- [ ] Drivers NVIDIA actualizados
- [ ] Ollama corriendo con GPU
- [ ] Modelos descargados (al menos mistral:7b)
- [ ] Cloudflare Tunnel configurado
- [ ] Servicios corriendo (`docker compose ps`)
- [ ] Interfaz web accesible
- [ ] Primer proyecto completado exitosamente

¡Listo! Tu sistema multi-agente está funcionando en tu Jetson Thor con acceso remoto seguro.
