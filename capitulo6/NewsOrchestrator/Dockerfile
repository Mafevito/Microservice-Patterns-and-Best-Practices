FROM python:3.6.1 
 
COPY . /app 
 
WORKDIR /app 
 
RUN pip install -r requirements.txt 
 
ENTRYPOINT ["python"] 
 
CMD ["app.py"] 
 
EXPOSE 5000


#El orquestador será una aplicación que utilice Flask como framework, pero no tendrá ninguna capa de comunicación con la base de datos. Los datos que este orquestador de microservicios utiliza no provienen de su propia base de datos, sino de otros microservicios que son consumidos por el agente de mensajería.