FROM python:3.6.1 
COPY . /app 
WORKDIR /app 
RUN pip install -r requirements.txt 
ENTRYPOINT ["python"] 
CMD ["app.py"] 
EXPOSE 5000

#En este archivo, hay dos puntos de atención. El primero es el archivo requirements.txt, que contiene todas las dependencias del proyecto. El segundo punto de atención es la exposición del puerto 5000, ya que allí se ejecuta el servidor de aplicaciones