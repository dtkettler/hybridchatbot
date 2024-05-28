import configparser
from abc import ABC, abstractmethod

from gpt import GPT


class LLM(ABC):

    @abstractmethod
    def run_llm(self, system_prompt, user_prompt, temperature=0.5, Json=False):
        pass

    @abstractmethod
    def run_llm_with_history(self, system_prompt, user_prompt, history, temperature=0.5, functions=False):
        pass

def get_llm():
    config = configparser.ConfigParser()
    config.read('config.ini')
    type = config['DEFAULT']['model_type']

    if type == "llamacpp":
        from llamacpp import Llamacpp

        model_repo = config['DEFAULT']['model_repo']
        model_file = config['DEFAULT']['model_file']
        gpu_layers = config.getint('DEFAULT', 'gpu_layers')
        template_format = config['DEFAULT']['template_format']

        return Llamacpp(model_repo, model_file, template_format, gpu_layers)
    elif type == "mlc":
        from mlcllm import MLCLLM

        model = config['DEFAULT']['model']
        device = config['DEFAULT']['device']
        return MLCLLM(model, device)
    elif type == "openai":
        model = config['DEFAULT']['model']
        return GPT(model)
