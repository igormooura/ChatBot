FROM node:18-alpine AS base
WORKDIR /usr/src/app
COPY package* .
RUN npm install

FROM base AS frontend-vite
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]