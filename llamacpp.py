import logging
import json
import outlines
from llama_cpp import Llama, llama_grammar
from animated_loader import AnimatedLoader


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.DEBUG)

# Phi-3's prompt format not yet supported in llama-cpp-python so we need to handle that one manually
phi3_prompt_template = """<|system|>
{system_prompt}<|end|>
{history}<|user|>
{user_prompt}<|end|>
<|assistant|>
"""
phi3_history_element = """<|user|>
{user}<|end|>
<|assistant|>
{assist}<|end|>
"""

class Llamacpp:
    def __init__(self, model_repo, model_file, template_format, gpu_layers):
        #self.model = outlines.models.llamacpp(model_repo, model_file, n_gpu_layers=gpu_layers)
        #self.model = outlines.models.llamacpp(model_repo, model_file)
        self.model = Llama.from_pretrained(repo_id=model_repo, filename=model_file, chat_format=template_format,
                                           verbose=False)
        self.template_format = template_format

    def run_model(self, messages, temperature=0.5, Json=False, schema=None):
        with AnimatedLoader():
            if self.template_format == "phi-3":
                history = ""
                user = ""
                assistant = ""
                for message in messages[1:-1]:
                    if message["role"] == "user":
                        user = message["content"]
                    elif message["role"] == "assistant":
                        assistant = message["content"]

                    if user and assistant:
                        history += phi3_history_element.format(user=user, assist=user)
                        user = ""
                        assistant = ""
                prompt = phi3_prompt_template.format(system_prompt=messages[0]["content"], history=history,
                                                     user_prompt=messages[-1]["content"])
                if schema:
                    grammar = llama_grammar.LlamaGrammar.from_json_schema(json.dumps(schema))
                    output = self.model.create_completion(prompt=prompt, grammar=grammar,
                                                          temperature=temperature)
                    formatted_output = json.loads(output['choices'][0]['text'])
                elif Json:
                    output = self.model.create_completion(prompt=prompt, response_format={"type": "json_object"},
                                                          temperature=temperature)
                    formatted_output = json.loads(output['choices'][0]['text'])
                else:
                    output = self.model.create_completion(prompt=prompt, temperature=temperature)
                    formatted_output = output['choices'][0]['text']
            else:
                if schema:
                    output = self.model.create_chat_completion(messages=messages, response_format={"type": "json_object",
                                                                                          "schema": schema},
                                                               temperature=temperature)
                    formatted_output = json.loads(output['choices'][0]['message']['content'])
                elif Json:
                    output = self.model.create_chat_completion(messages=messages, response_format={"type": "json_object"},
                                                               temperature=temperature)
                    formatted_output = json.loads(output['choices'][0]['message']['content'])
                else:
                    output = self.model.create_chat_completion(messages=messages, temperature=temperature)
                    formatted_output = output['choices'][0]['message']['content']

        return formatted_output

    def run_llm(self, system_prompt, user_prompt, temperature=0.5, Json=False):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.run_model(messages, temperature, Json=Json)

    def run_llm_with_history(self, system_prompt, user_prompt, history, temperature=0.5, schema=None):
        if schema:
            system_prompt += "\nJSON output should use the schema:\n{}".format(schema)

        messages = [{"role": "system", "content": system_prompt}]
        for message in history:
            messages.append({"role": "user", "content": message["user"]})
            messages.append({"role": "assistant", "content": message["assistant"]})
        messages.append({"role": "user", "content": user_prompt})

        return self.run_model(messages, temperature, schema=schema)
