import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import AdamW, Adam

# --- Configuración de rutas y parámetros ---
base_dir = r"D:/Residuos"
img_size = (224, 224)
batch_size = 16
epochs_inicial = 20
epochs_fine_tuning = 10

# --- Preparación de Datos con Aumentación ---
# Aumentamos un poco los rangos para obligar al modelo a generalizar mejor
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.15,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2
)

train_data = train_datagen.flow_from_directory(
    base_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_data = val_datagen.flow_from_directory(
    base_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

# --- Arquitectura del Modelo ---
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    # Dropout más agresivo para combatir el sobreajuste que vimos en tus logs
    layers.Dropout(0.5), 
    # Agregamos regularización L2 en la capa densa
    layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.001)),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(train_data.num_classes, activation='softmax', dtype='float32')
])

# --- Compilación Inicial ---
model.compile(
    optimizer=AdamW(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# --- Callbacks ---
callback_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=3,
    verbose=1
)

early_stop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True # Esto asegura que guardes el mejor modelo, no el último
)

# --- Entrenamiento Fase 1 (Solo cabeza del modelo) ---
print("\n🚀 Entrenando capas superiores...")
model.fit(
    train_data,
    validation_data=val_data,
    epochs=epochs_inicial,
    callbacks=[callback_lr, early_stop]
)

# --- Fase 2: Fine-tuning ---
print("\n🔧 Iniciando Fine-tuning...")
base_model.trainable = True

# Descongelamos solo las últimas 30 capas para un ajuste fino y evitar que el error suba
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=1e-5), # Rate muy bajo para no destruir los pesos de ImageNet
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_data, 
    validation_data=val_data, 
    epochs=epochs_fine_tuning,
    callbacks=[early_stop] # Reutilizamos early stopping por seguridad
)

# --- Guardado del Modelo ---
os.makedirs("modelo_entrenado1", exist_ok=True)
ruta_h5 = "modelo_entrenado1/clasificador_canecas.h5"
model.save(ruta_h5)

print("\n✅ Proceso completado")
print(f"📁 Modelo guardado en: {ruta_h5}")
print(f"🏷️ Clases detectadas: {list(train_data.class_indices.keys())}")