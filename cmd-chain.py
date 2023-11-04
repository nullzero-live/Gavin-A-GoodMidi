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
    """You are an expert level music composer. Generate the lyrics of a song named {song_name} that matches the following description. Make it catchy and suitable for a 4/4 rhythm 
    ******
    {song}
    ******
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
    """Take the {chords} and using MIDI notation. Write the synth, bass and drum MIDI notes as two dictionaries. One dictionary for the verse, one for the chorus.:
    Example:
    {Song Name: str,
    Element: str(Verse | Chorus),
     Synth: tuple(int,int),
     Bass: tuple(int,int),
     Drums: tuple(int, int)
     }

    Output only the dictionary, nothing else.
    """
)

prompt4 = ChatPromptTemplate.from_template(
    """Using MIDI notation Create a Dictionary of Lists with the Verse and Chorus Rhythm in 4/4 time:
    Verse: {Verse}
    Chorus: {Chorus}
    
    Example:
    {Verse:[],
    Chorus:[]}"""
)

model_parser = model | StrOutputParser()

describer = (
    {"song": RunnablePassthrough()} | prompt1 | {"color": model_parser}
)
color_to_fruit = prompt2 | model_parser
color_to_country = prompt3 | model_parser
question_generator = (
    color_generator | {"fruit": color_to_fruit, "country": color_to_country} | prompt4
)

prompt = question_generator.invoke("warm")
model.invoke(prompt)