import logging
import json
import outlines
from animated_loader import AnimatedLoader


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

class Llamacpp:
    def __init__(self, model_repo, model_file, template_format, gpu_layers):
        self.model = outlines.models.llamacpp(model_repo, model_file, n_gpu_layers=gpu_layers)
        self.model = outlines.models.llamacpp(model_repo, model_file)

        if template_format == "chatML":
            self.prompt_template = """<|im_start|>system
{system_prompt}<|im_end|>
{history}
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""
            self.history_element = """<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
{assist}<|im_end|>"""
        elif template_format == "phi":
            self.prompt_template = """<|system|>
{system_prompt}<|end|>
{history}
<|user|>
{user_prompt}
<|assistant|>
"""
            self.history_element = """<|user|>
{user}<|end|>
<|assistant|>
{assist}<|end|>
"""
        else:
            self.prompt_template = """<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{history} {user_prompt}[/INST]
"""
            self.history_element = """{user} [/INST] {assist} </s><s>[INST] """

    def run_model(self, prompt, temperature=0.5, Json=False, functions=None):
        with AnimatedLoader():
            if functions:
                generator = outlines.generate.json(self.model, json.dumps(functions[0]["parameters"]))
                output = generator(prompt)
            elif Json:
                # JSON without schema not implemented yet in this verison...
                pass
            else:
                generator = outlines.generate.text(self.model)
                output = generator(prompt)


        return output

    def run_llm(self, system_prompt, user_prompt, temperature=0.5, Json=False):
        prompt = self.prompt_template.format(system_prompt=system_prompt, history="", user_prompt=user_prompt)

        return self.run_model(prompt, temperature, Json=Json)

    def run_llm_with_history(self, system_prompt, user_prompt, history, temperature=0.5, functions=None):
        history_prompt = ""
        for message in history:
            history_prompt += self.history_element.format(user=message["user"], assist=message["assistant"])

        prompt = self.prompt_template.format(system_prompt=system_prompt, history=history_prompt,
                                             user_prompt=user_prompt)

        return self.run_model(prompt, temperature, functions=functions)
