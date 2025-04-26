FROM node:18

ENV PORT=3000

WORKDIR /frontend-react-js

COPY package*.json .

RUN npm install --verbose
COPY . .

EXPOSE ${PORT}
CMD ["npm", "start"]
