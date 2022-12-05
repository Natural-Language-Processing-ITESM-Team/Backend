from bertopic import BERTopic

modelo = BERTopic.load("BERTopicv1")

model_inference = modelo.find_topics(
    "hola me gustaria recibir informes para entrar al equipo de gaming"
)

print(model_inference)
