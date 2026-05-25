import tensorflow as tf
model = tf.keras.models.load_model("clasificador_canecas.h5", compile=False)
model.save("clasificador_canecas_compat.keras")
print("Listo:", model.input_shape)