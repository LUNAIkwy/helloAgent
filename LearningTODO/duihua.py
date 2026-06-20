import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List,Dict

load_dotenv()

class HelloAgentsLLM:
    def __init__(self, model:str=None, api_key:str=None, base_url:str=None,time_out:int=None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")
        time_out = time_out or int(os.getenv("LLM_TIME_OUT",60))
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=time_out)

    def run(self,messages:List[Dict[str,str]],temprature:float=0)->str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={
                    "type":"json_object"
                },
                messages=messages,
                temperature=temprature,
                stream=True
            )
            collected_content = []
            for chunk in response:
                if not chunk.choices:continue
                content = chunk.choices[0].delta.content
                collected_content.append(content)
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

if __name__ == "__main__":
    try:
        llm = HelloAgentsLLM()
        exampleMessages = [
            {"role":"system","content":"You are a helpful agent expert."},
            {"role":"user","content":"解释什么是agent"}
        ]             
        responseTxT = llm.run(messages=exampleMessages)
        if responseTxT:
            print(responseTxT)
    except Exception as e:
        print(f"{e}")