import threading

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager

from app.callbacks.streaming import ThreadedGenerator, ChainStreamHandler

from ..LLM.OpenCalm7B_LLM import OpenCalm7B_LLM


class OpenCalm7B_Chat:
    def __init__(self, history):
        self.template = """
        以下は、タスクを説明する指示と、文脈のある入力の組み合わせです。
        要求を適切に満たす応答を書きなさい。

        # 指示
        {input}

        # 出力'
        """
        self.prompt_template = PromptTemplate(
            input_variables=['input'],
            template=self.template,
        )

    def generator(self, user_message):
        g = ThreadedGenerator()
        threading.Thread(target=self.llm_thread, args=(g, user_message)).start()
        return g

    def llm_thread(self, g, user_message):
        try:
            llm = OpenCalm7B_LLM(callback_manager=CallbackManager([ChainStreamHandler(g)]))

            chain = LLMChain(
                llm=llm,
                prompt=self.prompt_template,
                verbose=True,
            )

            chain(user_message)
        finally:
            g.close()
