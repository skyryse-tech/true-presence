FROM node:18-alpine

WORKDIR /app

COPY frontend/admin-dashboard/package*.json ./

RUN npm install --omit=dev

COPY frontend/admin-dashboard/ .

RUN npm run build

RUN npm install -g serve

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD ["serve", "-s", "build", "-l", "3000"]
