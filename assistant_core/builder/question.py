from enum import Enum

from langchain_core.messages import AIMessage, HumanMessage

from assistant_core.builder import BaseBuilder, BuilderContext
from assistant_core.nodes import ProcessDataNode, QuestionNode
from assistant_core.state import QuestionState


class CreateQuestionNode(ProcessDataNode):
    def __init__(self, question_prompt: str, **kwargs):
        super().__init__(**kwargs)
        self.question_prompt = question_prompt

    async def __call__(self, state: dict, config) -> QuestionState:
        prompt = self.system_message(self.question_prompt)
        messages = state.get("messages", []) + [prompt]
        response = await self.model.ainvoke(messages, config=config)
        return {"question": response.content}


class ProcessAnswerNode(ProcessDataNode):
    async def __call__(self, state: QuestionState, config) -> QuestionState:
        return {
            "messages": [
                AIMessage(state["question"]),
                HumanMessage(state["answer"]),
            ]
        }


class QuestionBuilder(BaseBuilder):

    class Nodes(str, Enum):
        CREATE_QUESTION = "create_question"
        QUESTION = "question"
        PROCESS_ANSWER = "process_answer"

    def __init__(
        self,
        process_name: str,
        question_prompt: str,
        process_answer_node_cls=ProcessAnswerNode,
    ):
        self.process_name = process_name
        self.question_prompt = question_prompt
        self.process_answer_node_cls = process_answer_node_cls

    @classmethod
    def get_node_name(cls, node: Nodes, process_name: str) -> str:
        if node not in cls.Nodes:
            raise ValueError(f"Invalid node type: {node}")

        return f"{node.value}_{process_name}"

    def get_process_answer_node(
        self, node_name: str, context: BuilderContext
    ) -> ProcessAnswerNode:
        return self.process_answer_node_cls(
            name=node_name,
            model=context.model,
        )

    def build(self, context: BuilderContext) -> None:
        create_question_node = CreateQuestionNode(
            name=self.get_node_name(self.Nodes.CREATE_QUESTION, self.process_name),
            question_prompt=self.question_prompt,
            model=context.model,
        )

        question_node = QuestionNode(
            name=self.get_node_name(self.Nodes.QUESTION, self.process_name),
        )

        process_answer_node = self.get_process_answer_node(
            node_name=self.get_node_name(self.Nodes.PROCESS_ANSWER, self.process_name),
            context=context,
        )

        context.graph_builder.add_sequence(
            [
                (create_question_node.name, create_question_node),
                (question_node.name, question_node),
                (process_answer_node.name, process_answer_node),
            ]
        )

        context.graph_builder.add_edge(
            process_answer_node.name,
            context.resolver_node.name,
        )
