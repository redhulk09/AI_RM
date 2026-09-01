FROM node:22-alpine
WORKDIR /app
COPY frontend/package.json frontend/tsconfig.json frontend/next-env.d.ts frontend/postcss.config.mjs ./
RUN npm install
COPY frontend/app ./app
COPY frontend/components ./components
COPY frontend/lib ./lib
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start"]
