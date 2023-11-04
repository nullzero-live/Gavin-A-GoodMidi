import os
from dotenv import load_dotenv
import openai
import wandb
from langchain.chat_models import ChatOpenAI
from gen_logger.logger_util import setup_logger
from operator import itemgetter
from langchain.schema.runnable import RunnableParallel
from langchain.schema import StrOutputParser
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap, RunnablePassthrough


load_dotenv()

_logger=setup_logger("langllm")
os.environ["LANGCHAIN_WANDB_TRACING"] = "false"
os.environ["WANDB_PROJECT"] = "avin-midi"
_logger.info(f"{os.getenv('OPENAI_API_KEY')}")

try:
    wandb.login(key=os.getenv("WANDB_API_KEY"))
    wandb.init(project=os.getenv("WANDB_PROJECT"))
except Exception as e:
    _logger.error(e)

try:
    _logger.info(f"Adding openAI API key {os.getenv('OPENAI_API_KEY')}")
    model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")
    _logger.info("init llm complete")
except Exception as e:
    _logger.error(e)

song_description = "A warm and fuzzy pop hit" #input("Describe your song")
song_name = "Gavin A Good Test" #input('What would you like the name of your song to be?')
#song_structure = input("What structure would you like eg. AB|AB?")

def image_of_description(description):
    #Make an image of the song description
    image_req = openai.Image.create(prompt=f"A futuristic anime image with vibrant color of: {song_description}",
    n=2,
    size="1024x1024"
    )

    image_res = image_req["data"][0]
    print(image_res)
    return image_res






#Set of prompts
prompt1 = ChatPromptTemplate.from_template(
    """You are an expert level music composer. Generate the lyrics of a song named 'Gavin a Good Test.'
     The theme of the song will matche the following description. 
    Make it catchy and suitable for a 4/4 rhythm:
    ```{description}
    ```
    """
)
prompt2 = ChatPromptTemplate.from_template(
    """Take the song and write the piano chords for a Chorus and Verse. Write the chords and nothing else:
    {song}
    Example:
    Verse:
    Chorus:
    """    
)

#Can generate the colors of the song and make a User Interface.
prompt3 = ChatPromptTemplate.from_template(
    """Take the {chords} 
    
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
    Generate the rhythm MIDI notation for the {element} as list(tuple(int, int, int))
    Use 4/4 time in Traditional Western Notation.
    Insert the list into the dictionary created previously
    
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

describer = {"description": RunnablePassthrough()} | prompt1 | {"song": model_parser}

prompt = describer.invoke("this is a test")
print(model.invoke(prompt).replace("\n",""))

chords = ( {"song": prompt1} | prompt2 | {"chords:":model_parser} )
chords_to_midi = ( {"verse":itemgetter("verse"), "chorus":itemgetter("chorus")} | prompt3 | model_parser )
midi_to_rhythm = ( ( chords_to_midi| {"verse": itemgetter("verse")}, {"chorus": model_parser}) )
final_dicts = ( describer | {"dictionary": midi_to_rhythm, "output": midi_to_rhythm} | prompt5 )



#prompt = question_generator.invoke("warm")
#model.invoke(prompt)