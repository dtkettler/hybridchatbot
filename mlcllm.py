from mlc_llm import MLCEngine
import json
from animated_loader import AnimatedLoader


class MLCLLM:
    def __init__(self, model, device):
        self.engine = MLCEngine(model, device=device, mode="interactive")
        self.model = model

    def __del__(self):
        self.engine.terminate()

    def run_model(self, messages, temperature=0.5, Json=False, schema=None):
        with AnimatedLoader():
            if schema:
                responses = self.engine.chat.completions.create(messages=messages, model=self.model,
                                                                temperature=temperature,
                                                                response_format={"type": "json_object",
                                                                                 "schema": json.dumps(schema)},
                                                                stream=False)
                output = json.loads(responses.choices[0].message.content)["properties"]
            elif Json:
                responses = self.engine.chat.completions.create(messages=messages, model=self.model,
                                                                temperature=temperature,
                                                                response_format={"type": "json_object"}, stream=False)
                output = json.loads(responses.choices[0].message.content)["properties"]
            else:
                responses = self.engine.chat.completions.create(messages=messages, model=self.model,
                                                                temperature=temperature,
                                                                stream=False)
                output = responses.choices[0].message.content

        return output

    def run_llm(self, system_prompt, user_prompt, temperature=0.5, Json=False, schema=None):
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]

        return self.run_model(messages, temperature, Json=Json, schema=schema)

    def run_llm_with_history(self, system_prompt, user_prompt, history, temperature=0.5, functions=None):
        if functions:
            schema = functions[0]["parameters"]
        else:
            schema = None

        if schema:
            system_prompt += "\nJSON output should use the schema:\n{}".format(schema)

        messages = [{"role": "system", "content": system_prompt}]
        for message in history:
            messages.append({"role": "user", "content": message["user"]})
            messages.append({"role": "assistant", "content": message["assistant"]})
        messages.append({"role": "user", "content": user_prompt})

        return self.run_model(messages, temperature, schema=schema)
