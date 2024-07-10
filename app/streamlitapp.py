# Import all of the dependencies
import streamlit as st
import os 
import imageio 
import subprocess
import tensorflow as tf 
from utils import load_data, num_to_char
from modelutil import load_model

# Set the layout to the streamlit app as wide 
st.set_page_config(layout='wide')

# Setup the sidebar
with st.sidebar: 
    st.image('img1.png')
    st.title('LipReader')
    st.info('This application is originally developed from the LipNet deep learning model.')

st.title('LipNet Full Stack App') 

# Generating a list of options or videos 
options = os.listdir(os.path.join('..', 'data', 's1'))
selected_video = st.selectbox('Choose video', options)

# Generate two columns 
col1, col2 = st.columns(2)

if options: 

    # Rendering the video 
    with col1: 
        st.info('The video below displays the converted video in mp4 format')
        file_path = os.path.join('..','data','s1', selected_video)

        # Convert the video using ffmpeg
        converted_file_path = 'test_video1.mp4'
        ffmpeg_command = f'ffmpeg -i {file_path} -vcodec libx264 {converted_file_path} -y'
        
        # for testing purrpose
        # Write the command being executed
        #st.write(f'Executing command: {ffmpeg_command}')

        # Execute the ffmpeg command using subprocess
        try:
            result = subprocess.run(ffmpeg_command, shell=True, check=True, capture_output=True, text=True)
            # If we get any errors we run this commands to find out the reason
            #st.write('Conversion output:', result.stdout)
            #st.write('Conversion error (if any):', result.stderr)
        except subprocess.CalledProcessError as e:
            st.error(f'Video conversion failed: {e.stderr}')
            st.stop()
        except FileNotFoundError:
            st.error('ffmpeg is not installed or not found in PATH. Please install ffmpeg and add it to your system PATH.')
            st.stop()

        # Check if the conversion was successful
        if os.path.exists(converted_file_path):
            # Rendering inside of the app
            video = open(converted_file_path, 'rb') 
            video_bytes = video.read() 
            st.video(video_bytes)
        else:
            st.error('Video conversion failed. Please check the ffmpeg command.')


    with col2: 
        st.info('This is all the machine learning model sees when making a prediction')
        video, annotations = load_data(tf.convert_to_tensor(file_path))
        imageio.mimsave('animation.gif', video, fps=10)
        st.image('animation.gif', width=400) 

        st.info('This is the output of the machine learning model as tokens')
        model = load_model()
        yhat = model.predict(tf.expand_dims(video, axis=0))
        decoder = tf.keras.backend.ctc_decode(yhat, [75], greedy=True)[0][0].numpy()
        st.text(decoder)

        # Convert prediction to text
        st.info('Decode the raw tokens into words')
        converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode('utf-8')
        st.text(converted_prediction)
        
