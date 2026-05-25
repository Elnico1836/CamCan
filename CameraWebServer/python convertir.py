import tensorflow as tf
import numpy as np

# Carga con custom_objects para ignorar renorm
class FixedBatchNorm(tf.keras.layers.BatchNormalization):
    def __init__(self, **kwargs):
        kwargs.pop('renorm', None)
        kwargs.pop('renorm_clipping', None)
        kwargs.pop('renorm_momentum', None)
        super().__init__(**kwargs)

old_model = tf.keras.models.load_model(
    "clasificador_canecas.h5",
    compile=False,
    custom_objects={"BatchNormalization": FixedBatchNorm}
)

old_model.save("clasificador_canecas_compat.keras")
print("Listo:", old_model.input_shape)