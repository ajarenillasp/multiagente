FROM node:20-alpine

WORKDIR /app

# Copiar archivos de configuración
COPY package*.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY vite.config.js ./

# Instalar dependencias
RUN npm install

# Copiar resto del código
COPY . .

# Exponer puerto
EXPOSE 3000

# Comando para desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
