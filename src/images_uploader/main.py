import streamlit as st
import os
import numpy as np
import cv2

PATH_S3 = "images_for_processing"

# Check if the directory exists
if not os.path.exists(PATH_S3):
    # If it doesn't exist, create the directory
    os.makedirs(PATH_S3)
    print(f"Directory '{PATH_S3}' created successfully.")

def process_image(uploaded_file, image_path):
    try:
        img = np.array(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)  # bgr view

        #gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cv2.imwrite(image_path, img)
        return True
    except Exception as e:
        st.error(f"Ошибка при обработке фотографии: {e}")
        return False

st.title("Загрузка фотографий")

uploaded_files = st.file_uploader("Загрузите фотографии", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        # Process the uploaded image
        image_path = os.path.join(PATH_S3, uploaded_file.name)
        if process_image(uploaded_file, image_path):
            st.success(f"Фотография {uploaded_file.name} успешно загружена")
        else:
            st.error(f"Ошибка при обработке фотографии {uploaded_file.name}")