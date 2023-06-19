FROM node:lts-alpine

WORKDIR /app

RUN yarn global add vite && \
    yarn create vite --template vue-ts . && \
    yarn install


EXPOSE 8080

CMD ["yarn", "dev", "--host", "--port", "8080"]