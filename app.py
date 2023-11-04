import streamlit as st
from PIL import Image
from cmd_chain import image_of_description, song_description

header_image = Image.open('/Users/nullzero/Documents/repos/gitlab.com/audiato/avin-midi/public/fd1ba208-69ad-43f0-9c9f-70f803a44c11.webp')



# Placeholder functions to be called on button click and for streaming output.
def handle_midi_conversion(input_text):
    # Placeholder for the function that will handle the conversion
    # Replace the 'pass' with your logic to handle the MIDI conversion.
    pass

def stream_function():
    # Placeholder for the function that will stream data
    # Replace 'pass' with your streaming logic.
    pass

# Function to stream output in the output box continuously.
def stream_output(output_box):
    # This function will run in a loop when called to stream data to the output box.
    # Call your stream_function here and update the output box with the results.
    while True:
        output_data = stream_function()  # Get the data from your stream function
        output_box.empty()  # Clear the previous output
        output_box.text(output_data)  # Update the output box with new data

# Create the Streamlit interface
st.image(header_image,caption= "Avin",)
st.title("'Avin a Good MIDI")
st.subheader("MIDI interpreter based on natural language input")

# Text input box
user_song_desc = st.text_input("Describe your song", "")
user_song_name = st.text_input("Name your song", "")

# Submit button
if st.button('Submit'):
    handle_midi_conversion(user_input)

# Output box for displaying the streaming function's output
output_box = st.empty()  # Create an empty output box which will be filled by stream_output function
st.button('Start Streaming', on_click=stream_output, args=(output_box,))  # Button to start streaming

# MIDI section
st.header("MIDI")
# Output box for displaying results from the MIDI processing function
midi_output_box = st.empty()  # This will be used to display the output from the MIDI processing

#Image of description
st.header("Image of description")
st.image(image_of_description(song_description))
