import tensorflow as tf
import numpy as np

# Carga el modelo viejo solo para extraer los pesos
old_model = tf.keras.models.load_model("clasificador_canecas.h5", compile=False)

# Reconstruye la arquitectura limpia sin renorm
base_model = tf.keras.applications.MobileNetV2(
    weights=None, include_top=False, input_shape=(224, 224, 3)
)

new_model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation='relu',
        kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(4, activation='softmax', dtype='float32')
])

# Copia los pesos del modelo viejo al nuevo
new_model.set_weights(old_model.get_weights())

# Guarda en formato compatible
new_model.save("clasificador_canecas_compat.keras")
print("Listo:", new_model.input_shape)