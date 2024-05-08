FROM nginx:latest
RUN rm -rf /usr/share/nginx/html/index.html
COPY ./Lab_1/. /usr/share/nginx/html/
