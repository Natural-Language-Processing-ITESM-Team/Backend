
from bertopic import BERTopic
modelo = BERTopic.load("BERTopicv1")

print(modelo.find_topics("hola me gustaria recibir informes para entrar al equipo de gaming"))