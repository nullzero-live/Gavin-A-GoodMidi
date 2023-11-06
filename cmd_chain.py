import os
from datetime import datetime
import timeit
from dotenv import load_dotenv
import openai
import wandb
from langchain.chat_models import ChatOpenAI


#Logging etc
from gen_logger.logger_util import setup_logger
from langchain.globals import set_verbose
from langchain.callbacks import WandbCallbackHandler, StdOutCallbackHandler  
from langchain.callbacks import wandb_tracing_enabled
from logs.wandb_langchain import wandb_callback
import textstat
import spacy


from operator import itemgetter
from langchain.schema.runnable import RunnableParallel
from langchain.schema import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap, RunnablePassthrough


#Input placeholders 

load_dotenv()
_logger=setup_logger("langllm")
os.environ["LANGCHAIN_WANDB_TRACING"] = "true"
os.environ["WANDB_PROJECT"] = "avin-midi"


#Initialize WandB and set Langchain flag to verbose
try:
    wandb.login(key=os.getenv("WANDB_API_KEY"))
    wandb.init(project=os.getenv("WANDB_PROJECT"))
    set_verbose(True)
    
    #prediction_table = wandb.Table(columns=["logTime", "func" "prompt", "prompt_tokens", "completion", 
                                            #"completion_tokens", "time"])
except Exception as e:
    _logger.error(e)

try:
    _logger.info(f"Adding openAI API key")
    callbacks = [StdOutCallbackHandler(), wandb_callback]
    model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo", callbacks=callbacks)
    _logger.info("init llm complete")
except Exception as e:
    _logger.error(e)

def image_of_description(description):
    #Make an image of the song description
    image_req = openai.Image.create(prompt=f"A futuristic anime image vibrants representative of a song that is: {song_description}",
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
    """You are an expert level music composer. Generate the lyrics of a song named 'Gavin a Good Test.'
     The theme of the song will matche the following description. 
    Make it catchy and suitable for a 4/4 rhythm:
    ```{description}
    ```
    """
)
prompt2 = ChatPromptTemplate.from_template(
    """Take the song and write the piano chords for a Verse. Write the chords as a python list and nothing else:
    *****
    {song}
    *****
    Example:
    Verse: []
    """
)

#Can generate the colors of the song and make a User Interface.
prompt3 = ChatPromptTemplate.from_template(
    """Take the following chords:
    ********
    {chords}
    ********* 
    
    Use MIDI notation. Write the synth, bass and drum MIDI notes for the {element} with varying velocity.
    Output as a dictionary
    Leave Rhythm empty for the next step:

    Example:
    {Song Name: str,
    Element: str({element}),
     Synth: tuple(int,int),
     Bass: tuple(int,int),
     Drums: tuple(int, int)
     Rhythm: list
     }

    Output nothing else.
    """
)

prompt4 = ChatPromptTemplate.from_template(
    """
    Generate the rhythm MIDI notation for the {element} as:
    list(tuple(int, int, int))
    Use 4/4 time in Traditional Western Notation.
    Insert the list into the dictionary created previously:
    {midi_rhythm}
   
    Example:
    {Song Name: str,
    Element: str({element}),
     Synth: tuple(int,int),
     Bass: tuple(int,int),
     Drums: tuple(int, int)
     Rhythm: list({rhythm})
     }
      
    
    """
)

prompt5 = ChatPromptTemplate.from_template(
    """Cleanup any inconistencies. Remove unnecessary information.
    Output the {dictionary} 
    Output a JSON object. Nothing Else:
    {output}
 """   
)


model_parser = model | StrOutputParser()

describer = ({"description": RunnablePassthrough()} | prompt1 | {"song": model_parser})
chords = ( {"song": describer} | prompt2 | {"chords" : model_parser} )
chords_to_midi = {"element": "verse", "chords" : chords} | prompt3 | {"midi": model_parser}
midi_to_rhythm = ( {"element": "verse", "midi": chords_to_midi} |  {"rhythm": model_parser})
midi_dict = ( describer | {"dictionary": chords_to_midi} | prompt5 )
rhythm_dict = (describer | {"dictionary": midi_to_rhythm} | prompt5 )

midi_dict = midi_dict.invoke(chords_to_midi)
'''prediction_table args(ln34):
    logTime", "func" "prompt", "prompt_tokens", "completion", 
                                            "completion_tokens", "time"
'''

model.invoke(midi_dict)
wandb_callback.flush_tracker(midi_dict, name="midi_dict")
rhythm_dict = rhythm_dict.invoke(midi_to_rhythm)
wandb_callback.flush_tracker(rhythm_dict, name="rhythm_dict")


_logger.info(model.invoke(midi_to_rhythm))



print(midi_dict)
print(rhythm_dict)



#prompt = question_generator.invoke("warm")
#model.invoke(prompt)