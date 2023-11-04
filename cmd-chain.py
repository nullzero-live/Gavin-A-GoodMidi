import os
import wandb
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
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

try:
    wandb.login(key=os.getenv("WANDB_API_KEY"))
    wandb.init(project=os.getenv("WANDB_PROJECT"))
except Exception as e:
    _logger.error(e)

try:
    model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")
    _logger.info("init llm complete")
except Exception as e:
    _logger.error(e)

song_description = input("Describe your song")
song_name = input("What would you like the name of your song to be?")
song_structure = input("What structure would you like eg. AB|AB?")


#Set of prompts
prompt1 = ChatPromptTemplate.from_template(
    """You are an expert level music composer. Generate the lyrics of a song named {song_name} that matches the following description. 
    Make it catchy and suitable for a 4/4 rhythm 
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
    Output the {dictionary} dictionary as a JSON object. Nothing Else:
    {output}
 """   
)


model_parser = model | StrOutputParser()

describer = (
    {"song_name": song_name} | prompt1 | {"song": model_parser})
print(describer.invoke())
chords = {"song": prompt1} | prompt2 | {"chords:":model_parser}
chords_to_midi = {"verse":itemgetter("verse"), "chorus":itemgetter("chorus")} | prompt3 | model_parser
midi_to_rhythm = prompt4 | {"verse": itemgetter("verse")}, {"chorus": model_parser}
final_dicts = {"dictionary": , "country": color_to_country} | prompt4



#prompt = question_generator.invoke("warm")
#model.invoke(prompt)