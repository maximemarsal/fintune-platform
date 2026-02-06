# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Indiquer explicitement l'environnement
ENV NODE_ENV=production

# Copier uniquement les fichiers nécessaires pour l'installation des dépendances
COPY package.json package-lock.json ./

# Nettoyer le cache npm avant d'installer les dépendances
RUN npm cache clean --force && \
    npm install --no-audit --no-fund --legacy-peer-deps i18next-http-backend

# Copier le reste de l'application
COPY . .

# Vérifier que react-intersection-observer est bien installé
RUN npm list react-intersection-observer || npm install react-intersection-observer --save

# Construire l'application React
RUN npm run build

# Production stage
FROM nginx:alpine

# Copier le build final dans Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copier la config Nginx comme template
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Variables d'environnement par defaut
ENV PORT=80

# Expose le port (Railway utilise $PORT dynamiquement)
EXPOSE 80

# Utiliser envsubst pour substituer $PORT et lancer nginx
CMD ["/bin/sh", "-c", "envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
