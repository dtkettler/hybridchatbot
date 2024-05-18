from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from llama_cpp import LlamaGrammar, Llama
import time
import json
import logging
from animated_loader import AnimatedLoader


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

class Llamacpp:
    def __init__(self, model_path, n_gpu_layers, n_batch, template_format):

        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        with open("lib/json.gbnf") as f:
            self.grammar = LlamaGrammar.from_string(f.read())

        self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_batch=n_batch,
                f16_kv=True,
                max_tokens=5000,
                top_p=1,
                n_ctx=32000,
                verbose=True,
                callback_manager=callback_manager
            )

        if template_format == "chatML":
            self.prompt_template = """<|im_start|>system
{system_prompt}<|im_end|>
{history}
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""
            self.history_element = """<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
{}<|im_end|>"""
        else:
            self.prompt_template = """<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{history} {user_prompt}[/INST]
"""
            self.history_element = """{user} [/INST] {assist} </s><s>[INST] """

    def run_model(self, prompt, temperature=0.5, json=False):
        with AnimatedLoader():
            if json:
                result = self.llm(prompt, temperature=temperature, max_tokens=5000, grammar=self.grammar)
            else:
                result = self.llm(prompt, temperature=temperature, max_tokens=5000)

            self.llm.reset()

        return result['choices'][0]['text']

    def run_llm(self, system_prompt, user_prompt, temperature=0.5, json=False):
        prompt = self.prompt_template.format(system_prompt=system_prompt, history="", user_prompt=user_prompt)

        return self.run_model(prompt, temperature, json)

    def run_llm_with_history(self, system_prompt, user_prompt, history, temperature=0.5, json=False):

        history_prompt = ""
        for message in history:
            history_prompt += self.history_element.format(user=message["user"], assist=message["assistant"])

        prompt = self.prompt_template.format(system_prompt=system_prompt, history=history_prompt, user_prompt=user_prompt)

        return self.run_model(prompt, temperature, json)

