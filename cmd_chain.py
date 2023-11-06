import os
from datetime import datetime
import timeit
from dotenv import load_dotenv
import openai
from openai.error import AuthenticationError
import wandb
from langchain.chat_models import ChatOpenAI


#Logging etc
from gen_logger.logger_util import setup_logger
from langchain.globals import set_verbose
from langchain.callbacks import WandbCallbackHandler, StdOutCallbackHandler  
from langchain.callbacks import wandb_tracing_enabled
#from logs.wandb_langchain import wandb_callback
#from wandb_langchain import wandb_callback, callbacks
import textstat
import spacy


from operator import itemgetter
from langchain.schema.runnable import RunnableParallel
from langchain.schema import StrOutputParser
from langchain.schema.output_parser import JsonOutputParser
from langchain.schema import messages_to_dict 
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap, RunnablePassthrough

#Input placeholders 

load_dotenv()
_logger=setup_logger("langllm")
os.environ["LANGCHAIN_WANDB_TRACING"] = "false"
os.environ["WANDB_PROJECT"] = "avin-midi"
set_verbose(True)


#Initialize WandB and set Langchain flag to verbose
try:
    wandb.login(key=os.getenv("WANDB_API_KEY"))
    wandb.init(project=os.getenv("WANDB_PROJECT"))
    
    
    prediction_table = wandb.Table(columns=["logTime", "func" "prompt", "prompt_tokens", "completion", 
                                            "completion_tokens", "time"])
except Exception as e:
    _logger.error(e)

try:
    _logger.info(f"Adding openAI API key")
    #callbacks = [StdOutCallbackHandler(), wandb_callback]
    model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo") 
    _logger.info("init llm complete. Model is {}".format(model))
except AuthenticationError as e:
    _logger.error(e)

def image_of_description(description):
    #Make an image of the song description
    image_req = openai.Image.create(prompt=f"A futuristic anime image vibrants representative of a song that is: {description}",
    n=0,
    size="1024x1024"
    )

    image_res = image_req["data"][0]
    
    print(image_res)
    return image_res



'''
Prompt Templates for the chain of calls to the model of choice:



'''



prompt1 = ChatPromptTemplate.from_template(
    """You are an expert level music composer. Generate the lyrics of a song named {song_name}
    The lyrics of the song will matche the following description. 
    -Make it catchy and suitable for a 4/4 rhythm:
    The mood, tone and style is to be:
    ```{description}
    ```
    
    """
)
prompt2 = ChatPromptTemplate.from_template(
    """Take the song and write the piano chords for a Verse. Write the chords as a python list and nothing else:
    *****
    {song}
    *****
    
    """
)

#Can generate the colors of the song and make a User Interface.
prompt3 = ChatPromptTemplate.from_template(
    """Take the following chords:
    ********
    {chords}
    ********* 
    - Use MIDI notation. Write the synth, bass and drum MIDI notes for the {element} with varying velocity.
    Synth:
    Bass:
    Drum:
    Rhythm:
    - Leave Rhythm empty for the next step
    - Remove all new line characters "\n"
    
    Output nothing else but a JSON Object with the MIDI that corresponds to the chords.
    """)

prompt4 = ChatPromptTemplate.from_template(
    """
    What is the MIDI notation of the rhythm {element} and:
    {chords} as:
    
    list(tuple(int, int, int))
    Use 4/4 time in Traditional Western Notation at 65bpm.
    Match the rhythm to the song.
    Remove all new line characters "\n"
    Insert the data into the rhythm key of the MIDI JSON Object
    {midi_dict}
      
    Output nothing but a JSON Object with the MIDI that corresponds to the rhythm element of the song.
    """
)

prompt5 = ChatPromptTemplate.from_template(
    """Cleanup any inconistencies. Remove unnecessary information. Format correctly as JSON:
    input:
     {dictionary} 
    Output a JSON object. Nothing Else:
    
 """   
)
song_name = "Cherry Prick Ya Dick"
description = "A warm blues vibe"
model_parser = model | StrOutputParser()
json_parser = model | JsonOutputParser()

describer = {"description": RunnablePassthrough(), "song_name": RunnablePassthrough()} | prompt1 | {"song":model_parser}
describer.invoke({"description": description, "song_name": song_name})
chords =  {"song": describer} | prompt2 | model
chords_to_midi = {"element": itemgetter("element"), "chords": chords, "song_name": itemgetter("song_name") } | prompt3 | {"midi": json_parser}
midi_to_rhythm = {"element": itemgetter("element"), "rhythm_dict": chords_to_midi, "song_name": itemgetter(song_name)} | prompt4 | {"rhythm":json_parser}
midi_chain = {"dictionary": chords_to_midi} | prompt5 | json_parser
rhythm_chain = {"dictionary": midi_to_rhythm} | prompt5 | json_parser


final = chords.invoke({"description": description, "song_name": song_name})
print(final)
c2m = chords_to_midi.invoke({"element": itemgetter("element"), "chords":chords, "description": description, "song_name": song_name})
#final = messages_to_dict(midi_chain.invoke({"element": "verse", "description": description, "song_name": song_name}, config={"verbose": True}))
print(c2m)
m2r = midi_to_rhythm

print(midi_chain.invoke({"element":"verse", "description": description, "song_name": song_name}+'\n'))
print(rhythm_chain.invoke({"element":"verse", "description": description, "song_name": song_name}+'\n'))

'''midi_dict = midi_dict.invoke(chords_to_midi)
prediction_table args(ln34):
    logTime", "func" "prompt", "prompt_tokens", "completion", 
                                            "completion_tokens", "time"


model.invoke(midi_dict)
wandb_callback.flush_tracker(midi_dict, name="midi_dict")
rhythm_dict = rhythm_dict.invoke(midi_to_rhythm)
wandb_callback.flush_tracker(rhythm_dict, name="rhythm_dict")


_logger.info(model.invoke(midi_to_rhythm))'''

